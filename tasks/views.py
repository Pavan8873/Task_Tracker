from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from datetime import datetime, timedelta
from .models import Task
from .forms import TaskForm

# View to list current and carried forward tasks
def task_list(request):
    today = timezone.now().date()
    
    # Get tasks with a due date up to today
    tasks = Task.objects.filter(due_date__lte=today, completed=False).order_by('due_date')
    
    # Get carried forward tasks
    carried_forward_tasks = Task.objects.filter(carried_forward=True).order_by('due_date')
    
    context = {
        'tasks': tasks,
        'carried_forward_tasks': carried_forward_tasks,
    }
    return render(request, 'tasks/task_list.html', context)

# View to add a new task
def add_task(request):
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            form.save()  # Save the form data to create a new task
            return redirect('task_list')
    else:
        form = TaskForm()  # Show an empty form if the method is GET
    return render(request, 'tasks/add_task.html', {'form': form})

# View to update an existing task
def update_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)  # Get the task or return 404 if not found
    
    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            task = form.save(commit=False)  # Save form data but don't commit to DB yet
            task.completed = request.POST.get('completed') == 'on'  # Check if the task is completed
            task.carried_forward = not task.completed  # Mark as carried forward if not completed
            task.save()  # Save the updated task
            return redirect('task_list')
    else:
        form = TaskForm(instance=task)  # Show the form pre-filled with the task data
    
    return render(request, 'tasks/update_task.html', {'form': form, 'task': task})

# View to show monthly summary of completed and carried forward tasks
def monthly_summary(request):
    now = datetime.now()
    
    # Calculate the start and end of the current month
    month_start = now.replace(day=1)
    month_end = (month_start + timedelta(days=31)).replace(day=1) - timedelta(days=1)
    
    # Filter completed tasks in the current month
    completed_tasks = Task.objects.filter(
        completed=True,
        due_date__range=(month_start, month_end)
    )
    
    # Filter carried forward tasks in the current month
    carried_forward_tasks = Task.objects.filter(
        carried_forward=True,
        due_date__range=(month_start, month_end)
    )
    
    context = {
        'completed_tasks': completed_tasks,
        'carried_forward_tasks': carried_forward_tasks,
    }
    return render(request, 'tasks/monthly_summary.html', context)

# View for home page
def home(request):
    return render(request, 'home.html')
