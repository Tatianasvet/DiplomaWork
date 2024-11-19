from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from shop.models import Salesman
from .forms import SignUpForm, SalesmanSignUpForm,  LoginForm, ChangeSalesmanInfoForm


class Context:
    context = {}
    request = None


class Signup(Context):
    success = False

    def signup_page(self, request):
        self.request = request
        if self.request.method == 'POST':
            if self.request.GET.get('salesman') == 'true':
                self.__signup_salesman()
            else:
                self.__signup_user()
            if self.success:
                return redirect('home')
        return render(request, 'signup.html', self.context)

    def __signup_user(self):
        form = SignUpForm(self.request.POST)
        if form.is_valid():
            user = form.save()
            login(self.request, user)
            self.success = True
        else:
            self.context['error_message'] = form.errors

    def __signup_salesman(self):
        user_form = SignUpForm(self.request.POST)
        salesman_form = SalesmanSignUpForm(self.request.POST, self.request.FILES)
        if user_form.is_valid():
            if salesman_form.is_valid():
                user = user_form.save()
                login(self.request, user)
                Salesman.objects.create(user=user,
                                        phone=self.request.POST.get('phone'),
                                        photo=self.request.FILES['photo'],
                                        description=self.request.POST.get('description'))
                return redirect('home')
            else:
                self.context['error_message'] = salesman_form.errors
        else:
            self.context['error_message'] = user_form.errors


class Login(Context):
    def log_in_page(self, request):
        self.request = request
        form = LoginForm(data=self.request.POST or None)
        if self.request.method == 'POST':
            if form.is_valid():
                username = form.cleaned_data['username']
                password = form.cleaned_data['password']
                user = authenticate(username=username, password=password)
                if user is not None:
                    login(self.request, user)
                    return redirect('home')
                else:
                    self.context['error_message'] = form.errors
            else:
                self.context['error_message'] = form.errors
        return render(self.request, 'login.html', self.context)

    def log_out(self, request):
        self.request = request
        logout(self.request)
        return redirect('home')


class Change(Context):
    salesman = None

    def change_salesman_info(self, request):
        self.request = request
        self.salesman = Salesman.objects.get(user=self.request.user)
        self.context['salesman'] = self.salesman
        if self.request.method == 'POST':
            form = ChangeSalesmanInfoForm(self.request.POST)
            if form.is_valid():
                self.__change_first_name()
                self.__change_photo()
                self.__change_description()
                self.__change_phone()
                self.__change_email()
                self.salesman.user.save()
                self.salesman.save()
                return redirect('account')
            else:
                self.context['error_message'] = form.errors
        return render(self.request, 'change_personal_info.html', self.context)

    def __change_first_name(self):
        first_name = self.request.POST.get('first_name')
        if first_name:
            self.salesman.user.first_name = first_name
            self.salesman.moderate = False

    def __change_photo(self):
        if 'photo' not in self.request.POST.keys():
            self.salesman.photo = self.request.FILES['photo']
            self.salesman.moderate = False

    def __change_description(self):
        description = self.request.POST.get('description')
        if description:
            self.salesman.description = description
            self.salesman.moderate = False

    def __change_phone(self):
        phone = self.request.POST.get('phone')
        if phone:
            self.salesman.phone = phone

    def __change_email(self):
        email = self.request.POST.get('email')
        if email:
            self.salesman.user.email = email
