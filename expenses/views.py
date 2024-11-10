"""Views.py"""

import json
import calendar
from io import BytesIO
from datetime import datetime
from xhtml2pdf import pisa
from django.db.models import Sum
from django.db.models import Q
from django.http import HttpResponse
from django.template.loader import get_template
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.core.exceptions import ValidationError
from django.utils import timezone
from .forms import (CustomAuthenticationForm, CategoryForm, CustomUserCreationForm,
ExpenseFilterForm, ExpenseForm)
from .models import Expense, Category

def register_view(request):
    """register function"""
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Registration successful. Please log in.')
            return redirect('login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

def login_view(request):
    """login function"""
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('dashboard')
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = CustomAuthenticationForm()
    return render(request, 'registration/login.html', {'form': form})

@login_required
def logout_view(request):
    """logout function"""
    logout(request)
    return redirect('login')

@login_required
def dashboard(request):
    """dashboard function"""
    current_month = timezone.now().month
    expenses = Expense.objects.filter(user=request.user,
date__month=current_month).order_by('-date', '-id')[:5]
    total_expense = expenses.aggregate(Sum('amount'))['amount__sum'] or 0
    categories = list(expenses.values('category').annotate(total=Sum('amount')))
    chart_labels = [category['category'] for category in categories]
    chart_data = [float(category['total']) for category in categories]
    context = {
        'total_expense': total_expense,
        'expenses': expenses,
        'chart_labels': json.dumps(chart_labels),
        'chart_data': json.dumps(chart_data),
    }
    return render(request, 'expenses/dashboard.html', context)

@login_required
def add_expense(request):
    """add expense function"""
    if request.method == 'POST':
        form = ExpenseForm(request.POST, user=request.user)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.user = request.user
            expense.save()
            messages.success(request, 'Expense added successfully!')
            return redirect('dashboard')
    else:
        form = ExpenseForm(user=request.user)
    return render(request, 'expenses/add_expense.html', {'form': form})

@login_required
def manage_categories(request):
    """manage category function"""
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            category = form.save(commit=False)
            category.user = request.user
            try:
                category.save()
                messages.success(request, f'Category "{category.name}" added successfully.')
            except ValidationError as e:
                messages.error(request, str(e))
            return redirect('manage_categories')
    else:
        form = CategoryForm()
    categories = Category.objects.filter(user=request.user)
    return render(request, 'expenses/manage_categories.html',
{'form': form, 'categories': categories})

@login_required
def delete_category(request, category_id):
    """delete category function"""
    category = get_object_or_404(Category, id=category_id, user=request.user)
    if request.method == 'POST':
        category.delete()
        messages.success(request, f'Category "{category.name}" deleted successfully.')
        return redirect('manage_categories')
    return render(request, 'expenses/delete_category.html', {'category': category})

@login_required
def edit_expense(request, expense_id):
    """edit expense function"""
    expense = get_object_or_404(Expense, id=expense_id, user=request.user)
    if request.method == 'POST':
        form = ExpenseForm(request.POST, instance=expense, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Expense updated successfully.')
            return redirect('dashboard')
    else:
        form = ExpenseForm(instance=expense, user=request.user)
    return render(request, 'expenses/edit_expense.html', {'form': form, 'expense': expense})

@login_required
def delete_expense(request, expense_id):
    """delete expense function"""
    expense = get_object_or_404(Expense, id=expense_id, user=request.user)
    if request.method == 'POST':
        expense.delete()
        messages.success(request, 'Expense deleted successfully.')
        return redirect('dashboard')
    return render(request, 'expenses/delete_expense.html', {'expense': expense})

@login_required
def expense_chart(request):
    """expense chart function"""
    expenses = Expense.objects.filter(user=request.user)
    categories = expenses.values('category').annotate(total=Sum('amount'))
    labels = [category['category'] for category in categories]
    data = [float(category['total']) for category in categories]
    context = {
        'labels': json.dumps(labels),
        'data': json.dumps(data),
    }
    return render(request, 'expenses/expense_chart.html', context)

@login_required
def expense_history(request):
    """expense history function"""
    expenses = Expense.objects.filter(user=request.user).order_by('-date')
    form = ExpenseFilterForm(request.GET, user=request.user)
    if form.is_valid():
        start_date = form.cleaned_data.get('start_date')
        end_date = form.cleaned_data.get('end_date')
        category = form.cleaned_data.get('category')
        search_term = form.cleaned_data.get('search_term')
        if start_date:
            expenses = expenses.filter(date__gte=start_date)
        if end_date:
            expenses = expenses.filter(date__lte=end_date)
        if category:
            expenses = expenses.filter(category=category)
        if search_term:
            expenses = expenses.filter(Q(description__icontains=search_term) |
Q(category__icontains=search_term))
    paginator = Paginator(expenses, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
        'form': form}
    return render(request, 'expenses/expense_history.html', context)

@login_required
def reports(request):
    """reports function"""
    current_year = datetime.now().year
    year = int(request.GET.get('year', current_year))
    month = request.GET.get('month', None)
    expenses = Expense.objects.filter(user=request.user, date__year=year)
    if month:
        month = int(month)
        expenses = expenses.filter(date__month=month)
        days_in_month = calendar.monthrange(year, month)[1]
        labels = [str(day) for day in range(1, days_in_month + 1)]
        data = [0] * days_in_month
        for expense in expenses:
            data[expense.date.day - 1] += float(expense.amount)
    else:
        labels = [calendar.month_name[i] for i in range(1, 13)]
        data = [0] * 12
        for expense in expenses:
            data[expense.date.month - 1] += float(expense.amount)
    category_totals = expenses.values('category').annotate(total=Sum('amount')).order_by('-total')
    context = {
        'year': year,
        'month': month,
        'labels': json.dumps(labels),
        'data': json.dumps(data),
        'category_totals': category_totals,
        'total_expense': sum(data),
        'years': range(current_year - 5, current_year + 1),
        'months': [{'number': i, 'name': calendar.month_name[i]} for i in range(1, 13)],
    }
    return render(request, 'expenses/reports.html', context)

@login_required
def download_report(request):
    """download report function"""
    current_year = datetime.now().year
    year = int(request.GET.get('year', current_year))
    month = request.GET.get('month', None)
    expenses = Expense.objects.filter(user=request.user, date__year=year)
    if month:
        month = int(month)
        expenses = expenses.filter(date__month=month)
        period = f"{calendar.month_name[month]} {year}"
    else:
        period = f"Year {year}"
    category_totals = expenses.values('category').annotate(total=Sum('amount')).order_by('-total')
    context = {
        'year': year,
        'month': month,
        'period': period,
        'category_totals': category_totals,
        'total_expense': expenses.aggregate(Sum('amount'))['amount__sum'] or 0,
    }
    template = get_template('expenses/report_download.html')
    html = template.render(context)
    response = HttpResponse(content_type='application/pdf')
    response[
'Content-Disposition']=f'attachment; filename="expense_report_{year}_{month or "full"}.pdf"'
    pdf = BytesIO()
    pisa.CreatePDF(html, dest=pdf)
    response.write(pdf.getvalue())
    pdf.close()
    return response
