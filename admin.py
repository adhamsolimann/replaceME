from django.contrib import admin
from django import forms
from django.contrib.admin.decorators import display
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import Customer, Item, Material, Order, OrderDetail,ContactMessage,Usecase 
from django.urls import reverse
from django.utils.html import format_html


#customer inline admin descriptor --> will be used to add Customer fields to User Detail Page in the admin
class CustomerInline(admin.StackedInline):
    model = Customer
    can_delete = False
    verbose_name_plural = 'customers'

# add the CustomerInline to the User Detail Page 
class UserAdmin(BaseUserAdmin): 
    inlines = (CustomerInline,)

#The follwing classes are used to change the List View in the Admin Page --> which fields should be visible
class CustomerAdmin(admin.ModelAdmin):
    Model = Customer
    list_display = ('id', 'get_user_firstname', 'get_user_lastname', 'get_user_email')

    #display foreign fields from user in customer view
    @admin.display(ordering='user__first_name', description='First Name')
    def get_user_firstname(self, obj):
        return obj.user.first_name

    @admin.display(ordering='user__last_name', description='Last Name')
    def get_user_lastname(self, obj):
        return obj.user.last_name

    @admin.display(ordering='user__email', description='Email')    
    def get_user_email(self,obj):
        return obj.user.email

class MaterialAdmin(admin.ModelAdmin):
    Model = Material
    list_display = ('id', 'name', 'material_class','price')

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields["heat_conductivity"].label = "Wärmeleitfähigkeit (W/m*K)"
        form.base_fields["tensile_strength"].label = "Zugfestigkeit (N/mm^2)"
        form.base_fields["hardness"].label = "Härte (HV)"
        form.base_fields["heat_capacity"].label = "Spezifische Wärmekapazität (kJ/K*kg)"
        form.base_fields["electric_conductivity"].label = "Elektrische Leitfähigkeit (S/m)"
        form.base_fields["magnetism"].label = "Magnetisch ja/nein"
        form.base_fields["density"].label = "Dichte (g/cm^3)"
        form.base_fields["water_cunsumption"].label = "Wasserverbrauch (kg pro t)"
        form.base_fields["co2"].label = "CO2-Äquivalent (t CO2e)"
        form.base_fields["price"].label = "Preis (€ pro kg)"
        return form

class UsecaseAdmin(admin.ModelAdmin):
    Model = Usecase
    list_display = ('id','name', 'description') 
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields["heat_conductivity"].label = " Wärmeleitfähigkeit (W/m*K)"
        form.base_fields["tensile_strength"].label = " Zugfestigkeit (N/mm^2)"
        form.base_fields["hardness"].label = " Härte (HV)"
        form.base_fields["heat_capacity"].label = " Spezifische Wärmekapazität (kJ/K*kg)"
        form.base_fields["electric_conductivity"].label = " Elektrische Leitfähigkeit (S/m)"
        form.base_fields["magnetism"].label = "Magnetisch ja/nein"
        form.base_fields["density"].label = " Dichte (g/cm^3)"
        return form  


class OrderDetailsInline(admin.TabularInline):
    model = OrderDetail
    extra = 0

class OrderAdmin(admin.ModelAdmin):
    Model = Order
    list_display = ('id','status', 'date','customer') 
    inlines = [ OrderDetailsInline ]

class OrderDetailAdmin(admin.ModelAdmin):
    Model = OrderDetail
    list_display = ('id', 'item','order', 'quantity')     

    #display foreign fields from user in customer view
    @admin.display(ordering='user__first_name', description='First Name')
    def get_user_firstname(self, obj):
        return obj.user.first_name

    @admin.display(ordering='user__last_name', description='Last Name')
    def get_user_lastname(self, obj):
        return obj.user.last_name

    @admin.display(ordering='user__email', description='Email')    
    def get_user_email(self,obj):
        return obj.user.email

class ContactMessageAdmin(admin.ModelAdmin):
    Model = ContactMessage
    list_display = ('id', 'user', 'Email','Titel', 'Beschreibung')  

class ItemAdmin(admin.ModelAdmin):
    Model = Item
    list_display = ('id','description', 'inStock', 'view_material_link')    

    # display foreign field from material in item view
    @admin.display(ordering='material__name', description='Material')
    def get_material_name(self,obj):
        return obj.material.name

    def view_material_link(self, obj):
        link = reverse("admin:webShop_material_change", args=[obj.material_id])
        return format_html('<a href="{}">{}</a>', link, obj.material.name)
    view_material_link.short_description = 'Material'
       



# Register the models to the admin site
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(Material, MaterialAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(Usecase, UsecaseAdmin)
admin.site.register(Item, ItemAdmin)
admin.site.register(OrderDetail, OrderDetailAdmin)
admin.site.register(Customer, CustomerAdmin)
admin.site.register(ContactMessage, ContactMessageAdmin)