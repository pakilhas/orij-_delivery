from django.urls import path
from . import views

urlpatterns = [
    # Páginas principais
    path('', views.cardapio, name='cardapio'),
    path('carrinho/', views.carrinho, name='carrinho'),
    path('checkout/', views.checkout, name='checkout'),
    path('confirmacao/<int:pedido_id>/', views.confirmacao, name='confirmacao'),
    
    # Operações do Carrinho
    path('adicionar/<int:produto_id>/', views.adicionar_ao_carrinho, name='adicionar_ao_carrinho'),
    path('aumentar/<int:produto_id>/', views.aumentar_item, name='aumentar_item'),
    path('diminuir/<int:produto_id>/', views.diminuir_item, name='diminuir_item'),
    path('remover/<int:produto_id>/', views.remover_item, name='remover_item'),
    
    # Admin
    path('admin/pedidos/', views.admin_pedidos, name='admin_pedidos'),
    path('admin/atualizar-status/<int:pedido_id>/', views.atualizar_status, name='atualizar_status'),
]