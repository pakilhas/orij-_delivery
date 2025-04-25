from django.db import models

class Categoria(models.Model):
    nome = models.CharField(max_length=100)

class Produto(models.Model):
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE)
    nome = models.CharField(max_length=100)
    descricao = models.TextField()
    preco = models.DecimalField(max_digits=10, decimal_places=2)
    imagem = models.ImageField(upload_to='produtos/')
    disponivel = models.BooleanField(default=True)

class Pedido(models.Model):
    STATUS_CHOICES = [
        ('Pendente', 'Pendente'),
        ('Em Preparo', 'Em Preparo'),
        ('Entregue', 'Entregue'),
    ]
    cliente_nome = models.CharField(max_length=100)
    cliente_endereco = models.CharField(max_length=200)
    cliente_telefone = models.CharField(max_length=20)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pendente')
    criado_em = models.DateTimeField(auto_now_add=True)

class ItemPedido(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE)
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE)
    quantidade = models.PositiveIntegerField()
    observacao = models.TextField(blank=True, null=True)  # Adicione se necessário