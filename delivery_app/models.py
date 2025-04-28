from django.db import models
import uuid
from django.urls import reverse

class Categoria(models.Model):
    nome = models.CharField(max_length=100)
    
    def __str__(self):
        return self.nome

class Produto(models.Model):
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE)
    nome = models.CharField(max_length=100)
    descricao = models.TextField()
    preco = models.DecimalField(max_digits=10, decimal_places=2)
    imagem = models.ImageField(upload_to='produtos/')
    disponivel = models.BooleanField(default=True)
    
    def __str__(self):
        return self.nome

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
    tracking_token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    
    def __str__(self):
        return f"Pedido #{self.id} - {self.cliente_nome}"
    
    def get_absolute_url(self):
        return reverse('acompanhar_pedido', args=[str(self.tracking_token)])
    
    def clean(self):
        # Remove caracteres não numéricos do telefone
        self.cliente_telefone = ''.join(filter(str.isdigit, self.cliente_telefone))
        super().clean()

class ItemPedido(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE)
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE)
    quantidade = models.PositiveIntegerField()
    observacao = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.quantidade}x {self.produto.nome} (Pedido {self.pedido.id})"
    
    class Meta:
        verbose_name = "Item do Pedido"
        verbose_name_plural = "Itens dos Pedidos"