from django.shortcuts import render, redirect
from .models import Categoria, Produto, Pedido, ItemPedido
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.http import require_POST
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.db.models import Count, Sum
from urllib.parse import quote  # Import correto

# Views Públicas
def cardapio(request):
    categorias = Categoria.objects.all()
    return render(request, 'cardapio.html', {'categorias': categorias})

@require_POST
def adicionar_ao_carrinho(request, produto_id):
    produto = Produto.objects.get(id=produto_id)
    carrinho = request.session.get('carrinho', {})
    produto_id_str = str(produto_id)
    
    observacao = request.POST.get('observacao', '')
    
    if produto_id_str in carrinho:
        carrinho[produto_id_str]['quantidade'] += 1
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
        carrinho[produto_id_str]['quantidade'] += 1
        request.session['carrinho'] = carrinho
        request.session.modified = True
    
    return redirect('carrinho')

@require_POST
def diminuir_item(request, produto_id):
    produto_id_str = str(produto_id)
    carrinho = request.session.get('carrinho', {})
    
    if produto_id_str in carrinho:
        if carrinho[produto_id_str]['quantidade'] > 1:
            carrinho[produto_id_str]['quantidade'] -= 1
        else:
            del carrinho[produto_id_str]
        
        request.session['carrinho'] = carrinho
        request.session.modified = True
    
    return redirect('carrinho')

def checkout(request):
    if request.method == 'POST':
        carrinho = request.session.get('carrinho', {})
        
        try:
            pedido = Pedido.objects.create(
                cliente_nome=request.POST.get('nome', 'Cliente não identificado'),
                cliente_endereco=request.POST.get('endereco', 'Endereço não fornecido'),
                cliente_telefone=request.POST.get('telefone', ''),
                total=0,
                status='Pendente'
            )
            
            total = 0
            for produto_id_str, item_data in carrinho.items():
                produto = Produto.objects.get(id=int(produto_id_str))
                quantidade = item_data.get('quantidade', 1)
                
                ItemPedido.objects.create(
                    pedido=pedido,
                    produto=produto,
                    quantidade=quantidade,
                    observacao=item_data.get('observacao', '')
                )
                
                total += produto.preco * quantidade

            pedido.total = total
            pedido.save()
            
            # Corrigido: usando quote em vez de urlquote
            mensagem = (
                f"*Pedido Confirmado* 🎉\n\n"
                f"▫️ Nº Pedido: {pedido.id}\n"
                f"▫️ Cliente: {pedido.cliente_nome}\n"
                f"▫️ Total: R$ {pedido.total:.2f}\n\n"
                f"Acompanhe seu pedido:\n"
                f"{request.build_absolute_uri(pedido.get_absolute_url())}"
            )
            
            whatsapp_url = f"https://wa.me/55{pedido.cliente_telefone}?text={quote(mensagem)}"
            
            request.session['carrinho'] = {}
            return redirect(f"{reverse('confirmacao', args=[pedido.id])}?whatsapp_url={quote(whatsapp_url)}")
            
        except Exception as e:
            print(f"ERRO NO CHECKOUT: {str(e)}")
            return redirect('carrinho')
    
    return render(request, 'checkout.html')

def confirmacao(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id)
    return render(request, 'confirmacao.html', {
        'pedido': pedido,
        'whatsapp_url': request.GET.get('whatsapp_url', ''),
        'tracking_url': request.build_absolute_uri(pedido.get_absolute_url())
    })

def acompanhar_pedido(request, token):
    pedido = get_object_or_404(Pedido, tracking_token=token)
    return render(request, 'acompanhamento.html', {'pedido': pedido})

# delivery_app/views.py

@staff_member_required
def admin_pedidos(request):
    pedidos = Pedido.objects.all().order_by('-criado_em')
    
    # Filtros
    status = request.GET.get('status')
    if status:
        pedidos = pedidos.filter(status=status)
    
    # Estatísticas corrigidas
    status_counts = Pedido.objects.values('status').annotate(
        quantidade=Count('id'),  # Renomeado para quantidade
        valor_total=Sum('total')
    )
    
    context = {
        'pedidos': pedidos,
        'status_counts': status_counts,
        'status_filter': status or 'Todos'
    }
    return render(request, 'admin/pedidos.html', context)

@require_POST
def atualizar_status(request, pedido_id):
    if request.method == 'POST':
        pedido = get_object_or_404(Pedido, id=pedido_id)
        novo_status = request.POST.get('status')
        
        if pedido.status != novo_status:
            mensagem = (
                f"*Atualização do Pedido* 📦\n\n"
                f"▫️ Nº Pedido: {pedido.id}\n"
                f"▫️ Novo Status: {novo_status}\n\n"
                f"Acompanhe seu pedido:\n"
                f"{request.build_absolute_uri(pedido.get_absolute_url())}"
            )
            
            print(f"Enviar para {pedido.cliente_telefone}:\n{mensagem}")
            
            pedido.status = novo_status
            pedido.save()
        
        return redirect('admin_pedidos')