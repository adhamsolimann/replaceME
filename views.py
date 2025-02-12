from datetime import datetime, timedelta
from fractions import Fraction
from django.http.response import BadHeaderError
from django.shortcuts import redirect, render
from  django.http import HttpResponse, request, response
from django.contrib.auth import authenticate, login
from .forms import AddUseCaseForm, ContactForm, CustomerEditForm, LoginForm,UserEditForm,UseCaseForm
from .forms import UserRegistrationForm
from .forms import PreferencesForm
from .models import ContactMessage, Item, Order, OrderDetail, Usecase
from .models import Material
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.http import HttpResponseRedirect,HttpResponse
from django.contrib import messages
from . import forms,models
from django.views.generic import FormView
from django.db.models import Q
import io
from xhtml2pdf import pisa
from django.template.loader import get_template
from django.template import Context
from django.http import HttpResponse



# Create your views here.


def index(request):
    return contactView(request)

def contacted(request):
    return render(request, 'general/contacted.html')

def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            user = authenticate(
                username=cd['username'], password=cd['password'])
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return HttpResponse('Erfolgreich verifiziert! ')
                else:
                    return HttpResponse('Deaktiviertes Konto')
            else:
                return HttpResponse('Eigegebenen Daten nicht gültig!')
    else:
        form = LoginForm()
    return render(request, 'account/login.html', {'form': form})


def logout_view(request):
    logout(request)


def register(request):
    if request.method == 'POST':
        user_form = UserRegistrationForm(request.POST)

        if user_form.is_valid():
            # Create unsaved User object
            new_user = user_form.save(commit=False)
            # Set User given password
            new_user.set_password(user_form.cleaned_data['password'])
            # Save User  object
            new_user.save()

            return render(request,
                          'account/register_done.html',
                          {'new_user': new_user})
    else:
        user_form = UserRegistrationForm()
    return render(request, 'account/register.html', {'user_form': user_form})


def preferenceForm(request):
    form = PreferencesForm(request.POST or None)
    usecase_form = UseCaseForm(request.POST or None)
    context = {
        'form': form,
        'usecase_form': usecase_form
    }
    if form.is_valid() and usecase_form.is_valid():
        # get Data from the Form and create filter query - To-do Change Query to filter all fields
        material_form = form.cleaned_data['material']
        height_form = form.cleaned_data['height']
        width_form = form.cleaned_data['width']
        depth_form = form.cleaned_data['depth']
        inStock_form = form.cleaned_data['inStock']
        
        filtered_items = Item.objects.filter(height__gte=height_form, width__gte=width_form, depth__gte=depth_form,inStock__gte=inStock_form, material=material_form).prefetch_related("material")
        unfiltered_materials = Material.objects.all().exclude(name = material_form)
        all_Materials = Material.objects.all()
        focus_material = Material.objects.filter(name = material_form)
        unfiltered_items = Item.objects.all().exclude(material=material_form).prefetch_related("material")
        alt_options = []

        ####  Usecase Filter ####
        usecase_data = usecase_form.cleaned_data['usecase']
        

        if usecase_data != None:
            usecase = Usecase.objects.get(name = usecase_data)
            filtered_materials = []
            for unfilterd_material in unfiltered_materials:
                if unfilterd_material.density in usecase.density and unfilterd_material.magnetism == usecase.magnetism and unfilterd_material.heat_conductivity in usecase.heat_conductivity and unfilterd_material.tensile_strength in usecase.tensile_strength and unfilterd_material.hardness in usecase.hardness and unfilterd_material.heat_capacity in usecase.heat_capacity and unfilterd_material.electric_conductivity in usecase.electric_conductivity: 
                    filtered_materials.append(unfilterd_material)
        
            for item in unfiltered_items:
                for material in filtered_materials:
                    if item.material == material and item.height >= height_form and item.width >= width_form and item.depth >= depth_form and item.inStock > inStock_form and item not in filtered_items:
                        alt_options.append(item)
            sorted_sustainability_materials = sorted(alt_options, key = lambda t: t.material.calculate_sustainability())
            

        ######## Material Filter #####
        if usecase_data == None:
            print(f"I will compare with {focus_material[0].name}")
            compared_options = []
            #Normalize the materials
            heat_conductivity_max, tensile_strength_max, hardness_max, heat_capacity_max,electric_conductivity_max,magnetism_max,density_max = 0,0,0,0,0,0,0
            for material in all_Materials:
                if(material.heat_conductivity>heat_conductivity_max):
                    heat_conductivity_max = material.heat_conductivity
                if(material.tensile_strength>tensile_strength_max):
                    tensile_strength_max = material.tensile_strength
                if(material.hardness>hardness_max):
                    hardness_max = material.hardness
                if(material.heat_capacity>heat_capacity_max):
                    heat_capacity_max = material.heat_capacity
                if(material.electric_conductivity>electric_conductivity_max):
                    electric_conductivity_max = material.electric_conductivity
                if(material.magnetism>magnetism_max):
                    magnetism_max = material.magnetism
                if(material.density>density_max):
                    density_max = material.density
            print(heat_conductivity_max,tensile_strength_max,electric_conductivity_max)
            
            for unfiltered_material in unfiltered_materials:
                # Here [0] is used to access the first material of filtered items (cause they all have the same material)
                std_dev = (((focus_material[0].heat_conductivity - unfiltered_material.heat_conductivity)/heat_conductivity_max)**2 +
                ((focus_material[0].tensile_strength - unfiltered_material.tensile_strength)/tensile_strength_max)**2 +
                ((focus_material[0].hardness - unfiltered_material.hardness)/hardness_max)**2 + 
                ((focus_material[0].heat_capacity - unfiltered_material.heat_capacity)/heat_capacity_max)**2 +
                ((focus_material[0].electric_conductivity - unfiltered_material.electric_conductivity)/electric_conductivity_max)**2 +
                ((focus_material[0].magnetism - unfiltered_material.magnetism)/magnetism_max)**2 +
                ((focus_material[0].density - unfiltered_material.density)/density_max)**2) /(len(unfiltered_materials))
                # If Standard deviation is less than 0.3 and Obj is not duplicate, put it in alt_options list
                compared_options.append(std_dev)

            # Normalization and finding out the replaceable materials
            alpha = 0.1
            replaceable_materials = []

            norm = [float(i)/max(compared_options) for i in compared_options]
            while((len(replaceable_materials)<3 or len(alt_options)<5) and alpha<1):
                alt_options.clear()
                replaceable_materials.clear()
                alpha += 0.05
                for i in range(len(norm)):
                    if norm[i] < alpha:
                        replaceable_materials.append(unfiltered_materials[i])
                for item in unfiltered_items:
                    if item.material in replaceable_materials and item.height >= height_form and item.width >= width_form and item.depth >= depth_form and item.inStock > inStock_form and item not in filtered_items:
                        alt_options.append(item)
                print(f'materials: {len(replaceable_materials)}')
                print(f'alt_options: {len(alt_options)}')
                print(f"alpha is {alpha}")

                    # alt_options.append(unfiltered_items[i])
                

            sorted_sustainability_materials = sorted(alt_options, key = lambda t: t.material.calculate_sustainability())
            
        context["alt_options"] = sorted_sustainability_materials
        context["filtered_items"] = filtered_items
        return render(request, "postLogin/table.html", context)

    else:
        return render(request, "postLogin/preferences.html", context)


def table(request):
    items = Item.objects.all()
    return render(request, 'postLogin/table.html', {'items': items})


def warenkorb(request):
    if 'product_ids' in request.COOKIES:
        product_ids = request.COOKIES['product_ids']
        counter=product_ids.split('|')
        product_count_in_cart=len(set(counter))
    else:
        product_count_in_cart=0

    products=None
    total=0
    if 'product_ids' in request.COOKIES:
        product_ids = request.COOKIES['product_ids']
        if product_ids != "":
            product_id_in_cart=product_ids.split('|')
            products=models.Item.objects.all().filter(id__in = product_id_in_cart)


            for p in products:
                total=total+p.get_price()




    return render(request,'postLogin/warenkorb.html',{'products':products,'total':total,'product_count_in_cart':product_count_in_cart})

def warenkorbAdd_view(request,pk):
    products=models.Item.objects.all()

    if 'product_ids' in request.COOKIES:
        product_ids = request.COOKIES['product_ids']
        counter=product_ids.split('|')
        product_count_in_cart=len(set(counter))
    else:
        product_count_in_cart=1

    response = render(request, 'base.html')

    if 'product_ids' in request.COOKIES:
        product_ids = request.COOKIES['product_ids']
        if product_ids=="":
            product_ids=str(pk)
        else:
            product_ids=product_ids+"|"+str(pk)
        response.set_cookie('product_ids', product_ids)
    else:
        response.set_cookie('product_ids', pk)

    product=models.Item.objects.get(id=pk)
    messages.info(request, product.description + ' zum Warenkorb hinzugefügt!')

    return response

def warenkorbRemove_view(request,pk):
    if 'product_ids' in request.COOKIES:
        product_ids = request.COOKIES['product_ids']
        counter=product_ids.split('|')
        product_count_in_cart=len(set(counter))
    else:
        product_count_in_cart=0

    total=0
    if 'product_ids' in request.COOKIES:
        product_ids = request.COOKIES['product_ids']
        product_id_in_cart=product_ids.split('|')
        product_id_in_cart=list(set(product_id_in_cart))
        product_id_in_cart.remove(str(pk))
        products=models.Item.objects.all().filter(id__in = product_id_in_cart)

        for p in products:
            total=total+p.get_price()

        value=""
        for i in range(len(product_id_in_cart)):
            if i==0:
                value=value+product_id_in_cart[0]
            else:
                value=value+"|"+product_id_in_cart[i]
        response = render(request, 'postLogin/warenkorb.html',{'products':products,'total':total,'product_count_in_cart':product_count_in_cart})
        if value=="":
            response.delete_cookie('product_ids')
        response.set_cookie('product_ids',value)
        return response


def profil(request):
    if request.method == 'POST':
        user_form = UserEditForm(request.POST,instance=request.user)
        customer_form = CustomerEditForm(request.POST,instance=request.user.customer)
        if user_form.is_valid() and customer_form.is_valid:
            user_form.save()
            customer_form.save()
            messages.success(request, 'Daten erfolgreich geändert')
            return render(request,'postLogin/profil.html',{'user_form': user_form, 'customer_form': customer_form})
    else:
        user_form = UserEditForm(instance=request.user)
        customer_form = CustomerEditForm(instance=request.user.customer)
    return render(request, 'postLogin/profil.html', {'user_form': user_form, 'customer_form': customer_form})
    


def about(request):
    return render(request, "general/about.html")

def contactView(request):
    form = ContactForm(request.POST)
    context = {
        'form':form
    }
    if form.is_valid():
             # Create unsaved Contact Message object
            user = request.user
            contact_message = ContactMessage(user=user, Email=form.cleaned_data['Email'], Titel=form.cleaned_data['Titel'], Beschreibung=form.cleaned_data['Beschreibung'])
            contact_message.save()
            return render(request, "general/contacted.html")
    else:
        form = ContactForm()
    return render(request, "base.html", {'form': form})


def add_usecase_view(request):
    if request.method == 'POST':
        add_usecase_form = AddUseCaseForm(request.POST)
        usecase = Usecase.objects.all().filter(name = request.POST["name"])
    
        if(len(usecase)!=0):
            messages.error(request, 'Ein Usecase mit diesem Namen ist bereits vorhanden!')
            add_usecase_form = AddUseCaseForm()
            return render(request, "postLogin/add_usecase.html", {'form': add_usecase_form})
        elif add_usecase_form.is_valid():
            # Create unsaved Usecase object
            add_usecase_form.save()
            return redirect(preferenceForm)
        else:
            messages.error(request, 'Bitte korrekte Daten eingeben. Alle maximalen Wert müssen größer sein als die minimalen Werte')
            add_usecase_form = AddUseCaseForm()
            return render(request, "postLogin/add_usecase.html", {'form': add_usecase_form})
    else:
        add_usecase_form = AddUseCaseForm()
    return render(request, "postLogin/add_usecase.html", {'form': add_usecase_form})
    
def payment_view(request):
    user = request.user
    current_date = datetime.now().date()
    total=0
    if 'product_ids' in request.COOKIES:
        product_ids = request.COOKIES['product_ids']
        if product_ids != "":
            product_id_in_cart=product_ids.split('|')
            products=models.Item.objects.all().filter(id__in = product_id_in_cart)


            for p in products:
                total=total+p.get_price()

    new_order = Order(customer=user,date=current_date,status=Order.AUFGEGEBEN,total_price=total)
    new_order.save()

    if 'product_ids' in request.COOKIES:
        product_ids = request.COOKIES['product_ids']
        if product_ids != "":
            product_id_in_cart=product_ids.split('|')
            products=models.Item.objects.all().filter(id__in = product_id_in_cart)


            for p in products:
                line_item = OrderDetail(order = new_order, item = p, quantity = p.inStock, price = p.get_price())
                line_item.save()
    response = render(request,'postLogin/payment.html')
    return response



def convertToPDF(template_src, context_dict):
    template = get_template(template_src)
    html  = template.render(context_dict)
    result = io.BytesIO()
    pdf = pisa.pisaDocument(io.BytesIO(html.encode("ISO-8859-1")), result)
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    return


def download_view(request):
    user = request.user
    date = datetime.now().date()
    frist = date + timedelta(7)

    if 'product_ids' in request.COOKIES:
        product_ids = request.COOKIES['product_ids']
        counter=product_ids.split('|')
        product_count_in_cart=len(set(counter))
    else:
        product_count_in_cart=0

    products=None
    total=0

    if 'product_ids' in request.COOKIES:
        product_ids = request.COOKIES['product_ids']
        if product_ids != "":
            product_id_in_cart=product_ids.split('|')
            products=models.Item.objects.all().filter(id__in = product_id_in_cart)

            for p in products:
                total=total+p.get_price()
    else:
        products= ""


    mydict = {
                    'products': products, 'totals': total, 'user': user, 'date': date, 'frist': frist
                }
    response = convertToPDF('postLogin/pdf.html',mydict)
    for p in products:
        p.inStock = 0
        p.save()

    response.delete_cookie('product_ids')
    return response

def orders_view(request):
    user = request.user
    orders = Order.objects.filter(customer = user)
    context = {'orders' : orders}
    return render(request, "postLogin/orders.html",context)

def orderDetails_view(request,id):
    order = Order.objects.get(pk=id)
    orderDetails = OrderDetail.objects.filter(order = order)
    context = {'orderDetails': orderDetails}
    return render(request, "postLogin/orderDetails.html",context)
