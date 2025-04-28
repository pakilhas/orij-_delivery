from django.contrib import admin
from .models import Categoria, Produto, Pedido, ItemPedido

class ItemPedidoInline(admin.TabularInline):
    model = ItemPedido
    extra = 0
    fields = ('produto', 'quantidade', 'observacao')
    readonly_fields = ('produto', 'quantidade', 'observacao')
    can_delete = False

@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ('id', 'cliente_nome', 'status', 'total', 'criado_em', 'tracking_link')
    list_filter = ('status', 'criado_em')
    search_fields = ('cliente_nome', 'cliente_telefone', 'id')
    readonly_fields = ('tracking_token', 'criado_em', 'total')
    inlines = [ItemPedidoInline]
    
    def tracking_link(self, obj):
        return f"/pedido/{obj.tracking_token}/"
    tracking_link.short_description = 'Link de Acompanhamento'

@admin.register(ItemPedido)
class ItemPedidoAdmin(admin.ModelAdmin):
    list_display = ('pedido', 'produto', 'quantidade', 'observacao_resumida')
    list_filter = ('pedido__status',)
    search_fields = ('produto__nome', 'pedido__id')

    def observacao_resumida(self, obj):
        return obj.observacao[:30] + '...' if obj.observacao else '-'
    observacao_resumida.short_description = 'Observação'

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'quantidade_produtos')
    search_fields = ('nome',)

    def quantidade_produtos(self, obj):
        return obj.produto_set.count()
    quantidade_produtos.short_description = 'Qtd. Produtos'

@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'categoria', 'preco', 'disponivel')
    list_filter = ('categoria', 'disponivel')
    search_fields = ('nome', 'descricao')
    list_editable = ('preco', 'disponivel')