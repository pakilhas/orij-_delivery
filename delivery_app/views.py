from django.shortcuts import render, redirect
from .models import Categoria, Produto, Pedido, ItemPedido
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.http import require_POST

# Views Públicas
def cardapio(request):
    categorias = Categoria.objects.all()
    return render(request, 'cardapio.html', {'categorias': categorias})

@require_POST
def adicionar_ao_carrinho(request, produto_id):
    produto = Produto.objects.get(id=produto_id)
    carrinho = request.session.get('carrinho', {})
    produto_id_str = str(produto_id)
    
    # Obter observação do formulário
    observacao = request.POST.get('observacao', '')
    
    # Estrutura do item no carrinho
    if produto_id_str in carrinho:
        carrinho[produto_id_str]['quantidade'] += 1
        # Mantém a observação se já existir, atualiza se nova
        if observacao:
            carrinho[produto_id_str]['observacao'] = observacao
    else:
        carrinho[produto_id_str] = {
            'quantidade': 1,
            'observacao': observacao
        }
    
    request.session['carrinho'] = carrinho
    return redirect('cardapio')

def carrinho(request):
    carrinho = request.session.get('carrinho', {})
    # Convertendo strings para inteiros
    produto_ids = [int(id) for id in carrinho.keys()]
    produtos = Produto.objects.filter(id__in=produto_ids)
    
    itens = []
    total = 0
    for produto in produtos:
        item_data = carrinho[str(produto.id)]
        quantidade = item_data['quantidade']
        observacao = item_data.get('observacao', '')
        
        subtotal = produto.preco * quantidade
        total += subtotal
        
        itens.append({
            'produto': produto,
            'quantidade': quantidade,
            'subtotal': subtotal,
            'observacao': observacao
        })
    
    return render(request, 'carrinho.html', {
        'itens': itens,
        'total': total
    })

@require_POST
def remover_item(request, produto_id):
    produto_id_str = str(produto_id)
    carrinho = request.session.get('carrinho', {})
    
    if produto_id_str in carrinho:
        del carrinho[produto_id_str]
        request.session['carrinho'] = carrinho
        request.session.modified = True
    
    return redirect('carrinho')

@require_POST
def aumentar_item(request, produto_id):
    produto_id_str = str(produto_id)
    carrinho = request.session.get('carrinho', {})
    
    if produto_id_str in carrinho:
        carrinho[produto_id_str]['quantidade'] += 1  # Corrigido aqui
        request.session['carrinho'] = carrinho
        request.session.modified = True
    
    return redirect('carrinho')

@require_POST
def diminuir_item(request, produto_id):
    produto_id_str = str(produto_id)
    carrinho = request.session.get('carrinho', {})
    
    if produto_id_str in carrinho:
        if carrinho[produto_id_str]['quantidade'] > 1:  # Corrigido aqui
            carrinho[produto_id_str]['quantidade'] -= 1  # Corrigido aqui
        else:
            del carrinho[produto_id_str]
        
        request.session['carrinho'] = carrinho
        request.session.modified = True
    
    return redirect('carrinho')

# Checkout e Confirmação
def checkout(request):
    if request.method == 'POST':
        carrinho = request.session.get('carrinho', {})
        pedido = Pedido.objects.create(
            cliente_nome=request.POST.get('nome'),
            cliente_endereco=request.POST.get('endereco'),
            cliente_telefone=request.POST.get('telefone'),
            total=0
        )
        
        total = 0
        for produto_id, quantidade in carrinho.items():
            produto = Produto.objects.get(id=produto_id)
            ItemPedido.objects.create(
                pedido=pedido,
                produto=produto,
                quantidade=quantidade
            )
            total += produto.preco * quantidade
        
        pedido.total = total
        pedido.save()
        request.session['carrinho'] = {}
        return redirect('confirmacao', pedido_id=pedido.id)
    
    return render(request, 'checkout.html')

def confirmacao(request, pedido_id):
    pedido = Pedido.objects.get(id=pedido_id)
    return render(request, 'confirmacao.html', {'pedido': pedido})

# Admin
@staff_member_required
def admin_pedidos(request):
    pedidos = Pedido.objects.all().order_by('-criado_em')
    return render(request, 'admin/admin_pedidos.html', {'pedidos': pedidos})

@require_POST
def atualizar_status(request, pedido_id):
    if request.method == 'POST':
        pedido = Pedido.objects.get(id=pedido_id)
        pedido.status = request.POST.get('status')
        pedido.save()
    return redirect('admin_pedidos')