from django.contrib.auth import get_user_model
from django.views.generic import CreateView
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views import View
from django.db.models import Q, F, BooleanField, Case, When, Sum
from django.db import transaction
from django.contrib import messages
# from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from coinapp.models import Transaction, Offering
from coinapp.forms import SignUpForm
# Create your views here.
User = get_user_model()

class SignUpView(CreateView):
    form_class = SignUpForm
    success_url = reverse_lazy("coinapp:home")
    template_name = "registration/signup.html"

@method_decorator(login_required, name="dispatch")
class HomeView(View):
    template_name = "home.html"

    def get(self, request):
        transactions = (
            Transaction.objects.filter(
                Q(creator_person=request.user) | Q(target_person=request.user)
            )
            .select_related("creator_person", "target_person","offering")
            .annotate(
                is_received=Case(
                    When(Q(creator_person=request.user), then=False),
                    default=True,
                    output_field=BooleanField(),
                )
            )
            .order_by("-created_at")
        )
        users = User.objects.exclude(username=request.user.username)
        total = User.objects.aggregate(total=Sum("amount"))
        return render(
            request, "home.html", {"transactions": transactions, "users": users,"total": total}
        )

    def post(self, request):
        touser = User.objects.get(username=request.POST["touser"])
        fromuser = request.user
        
        if touser == fromuser:
            messages.warning(
                request, "Error! You cannot send funds to your own account."
            )
        else:
            
            offering = Offering.objects.get(id = request.POST["offering"])
            with transaction.atomic():
                touser.amount = F("amount") + offering.amount
                fromuser.amount = F("amount") - offering.amount
                touser.save()
                fromuser.save()
                txn = Transaction.objects.create(
                    creator_person=fromuser, target_person=touser, offering=offering
                )
                messages.success(request, f"Success! Payment success. txnId:{txn.id}")
        
        return redirect("coinapp:home")


@login_required
def offering_view(request):
    return render(request, "coinapp/offerings.html",{"offerings":Offering.objects.order_by('category')})

@login_required
def load_offerings(request):
    username = request.GET.get('userid')
    offerings = []
    if username:
        offerings = Offering.objects.filter(user__username=username) # User.objects.get(username=username).offerings.all()
    return render(request, 'coinapp/user_offerings_list_options.html', {'offerings': offerings})