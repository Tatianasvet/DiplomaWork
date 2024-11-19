from django.shortcuts import render
from django.core.mail import send_mail
from .forms import MailForm


class Context:
    context = {}
    request = None


class Info:
    def about_page(self, request):
        return render(request, 'about.html')

    def faq_page(self, request):
        return render(request, 'dummy.html')

    def conditions_page(self, request):
        return render(request, 'dummy.html')

    def payment_page(self, request):
        return render(request, 'dummy.html')


class Contact(Context):

    def contact_page(self, request):
        self.request = request
        self.context['success'] = False
        if self.request.method == 'POST':
            form = MailForm(data=self.request.POST)
            if form.is_valid():
                self.__send_email()
            else:
                self.context['error_message'] = form.errors
        return render(self.request, 'contact.html', self.context)

    def __send_email(self):
        message = self.__create_email_message()
        if send_mail(subject=self.request.POST.get('subject'),
                     message=message,
                     from_email='svet_tan@mail.ru',
                     recipient_list=['manufakture@bk.ru']) == 1:
            self.context['success'] = True

    def __create_email_message(self):
        name = self.request.POST.get('name')
        back_email = self.request.POST.get('email')
        self.context['back_email'] = back_email
        message = (self.request.POST.get('message') +
                   f'\n\n-----\nС уважением, {name}\n{back_email}')
        if not self.request.user.is_anonymous:
            if self.request.user.first_name is not None:
                message += (f'\n\n-----\nОтправлено мастером: {self.request.user.first_name}\n'
                            f'username: {self.request.user.username}')
            else:
                message += f'\n\n-----\nОтправлено пользователем: {self.request.user.username}'
        else:
            message = 'АНОНИМНЫЙ ПОЛЬЗОВАТЕЛЬ ОТПРАВИЛ ПИСЬМО.\nТАК БЫТЬ НЕ ДОЛЖНО!!!'
        return message
