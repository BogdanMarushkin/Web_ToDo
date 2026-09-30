import React, { useEffect, useState } from 'react';
import axios from 'axios';
import './App.css';

const API_BASE_URL = 'http://localhost:8080';

function getTaskTitle(task) {
  return task.title ?? task.text ?? '';
}

function getTaskCompleted(task) {
  return Boolean(task.done ?? task.completed ?? task.is_done ?? false);
}

function getTaskCategoryId(task) {
  return task.category_id ?? task.category?.id ?? '';
}

// Имя категории: сначала из самой задачи (если бэкенд вложил объект), затем из списка категорий
function getTaskCategoryLabel(task, categoryNameById) {
  const categoryId = getTaskCategoryId(task);
  if (!categoryId) return '';
  return (
    task.category?.name ??
    task.category_name ??
    categoryNameById.get(categoryId) ??
    'Неизвестная категория'
  );
}

function completedPayload(value) {
  return { completed: value };
}

function getCategoryName(category) {
  return category.name ?? category.title ?? '';
}

function getErrorText(error) {
  const msg = error.response?.data?.detail;
  if (typeof msg === 'string') return msg;
  if (Array.isArray(msg)) return msg.map((item) => item?.msg ?? item).join(', ');
  return 'Ошибка запроса';
}

function App() {
  const [activeView, setActiveView] = useState('tasks');

  const [taskTitle, setTaskTitle] = useState('');
  const [isCompleted, setIsCompleted] = useState(false);
  const [taskCategoryId, setTaskCategoryId] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('all');
  const [tasks, setTasks] = useState([]);
  const [editingTaskId, setEditingTaskId] = useState(null);
  const [editingTaskOriginal, setEditingTaskOriginal] = useState(null);
  const [taskStatusMessage, setTaskStatusMessage] = useState('');

  const [categoryName, setCategoryName] = useState('');
  const [categories, setCategories] = useState([]);
  const [editingCategoryId, setEditingCategoryId] = useState(null);
  const [editingCategoryOriginal, setEditingCategoryOriginal] = useState(null);
  const [categoryStatusMessage, setCategoryStatusMessage] = useState('');

  const categoryNameById = new Map(
    categories.map((category) => [category.id, getCategoryName(category)])
  );

  const visibleTasks = tasks.filter((task) => {
    if (categoryFilter === 'all') return true;
    const categoryId = getTaskCategoryId(task);
    if (categoryFilter === 'none') return !categoryId;
    return categoryId === categoryFilter;
  });

  const completedCount = visibleTasks.filter((task) => getTaskCompleted(task)).length;
  const pendingCount = visibleTasks.length - completedCount;

  useEffect(() => {
    fetchTasks();
    fetchCategories();
  }, []);

  const fetchTasks = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/tasks`);
      setTasks(Array.isArray(response.data) ? response.data : []);
    } catch (error) {
      console.error('Error fetching tasks:', error);
      setTaskStatusMessage('Ошибка при загрузке задач');
    }
  };

  const fetchCategories = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/categories`);
      setCategories(Array.isArray(response.data) ? response.data : []);
    } catch (error) {
      console.error('Error fetching categories:', error);
      setCategoryStatusMessage('Ошибка при загрузке категорий');
    }
  };

  const resetTaskForm = () => {
    setTaskTitle('');
    setIsCompleted(false);
    setTaskCategoryId('');
    setEditingTaskId(null);
    setEditingTaskOriginal(null);
  };

  const resetCategoryForm = () => {
    setCategoryName('');
    setEditingCategoryId(null);
    setEditingCategoryOriginal(null);
  };

  const handleTaskSubmit = async () => {
    const title = taskTitle.trim();
    if (!title) return;

    try {
      if (editingTaskId) {
        const patchData = {};

        if (!editingTaskOriginal || title !== editingTaskOriginal.title) {
          patchData.title = title;
        }
        if (!editingTaskOriginal || isCompleted !== editingTaskOriginal.completed) {
          Object.assign(patchData, completedPayload(isCompleted));
        }
        if (!editingTaskOriginal || taskCategoryId !== editingTaskOriginal.categoryId) {
          // Пустая строка = "без категории" -> отправляем null
          patchData.category_id = taskCategoryId || null;
        }

        if (Object.keys(patchData).length === 0) {
          setTaskStatusMessage('Изменений нет');
          return;
        }

        await axios.patch(`${API_BASE_URL}/tasks/${editingTaskId}`, patchData);
        setTaskStatusMessage('Задача обновлена');
      } else {
        const payload = { title };
        if (taskCategoryId) {
          payload.category_id = taskCategoryId;
        }
        await axios.post(`${API_BASE_URL}/tasks`, payload);
        setTaskStatusMessage('Задача создана');
      }

      resetTaskForm();
      fetchTasks();
    } catch (error) {
      console.error('Error submitting task:', error);
      setTaskStatusMessage(`Ошибка: ${getErrorText(error)}`);
    }
  };

  const handleCategorySubmit = async () => {
    const name = categoryName.trim();
    if (!name) return;

    try {
      if (editingCategoryId) {
        const patchData = {};

        if (!editingCategoryOriginal || name !== editingCategoryOriginal.name) {
          patchData.name = name;
        }

        if (Object.keys(patchData).length === 0) {
          setCategoryStatusMessage('Изменений нет');
          return;
        }

        await axios.patch(`${API_BASE_URL}/categories/${editingCategoryId}`, patchData);
        setCategoryStatusMessage('Категория обновлена');
      } else {
        await axios.post(`${API_BASE_URL}/categories`, { name });
        setCategoryStatusMessage('Категория создана');
      }

      resetCategoryForm();
      fetchCategories();
    } catch (error) {
      console.error('Error submitting category:', error);
      setCategoryStatusMessage(`Ошибка: ${getErrorText(error)}`);
    }
  };

  const handleTaskEdit = (task) => {
    const originalTitle = getTaskTitle(task);
    const originalCompleted = getTaskCompleted(task);
    const originalCategoryId = getTaskCategoryId(task);

    setTaskTitle(originalTitle);
    setIsCompleted(originalCompleted);
    setTaskCategoryId(originalCategoryId);
    setEditingTaskId(task.id);
    setEditingTaskOriginal({
      title: originalTitle,
      completed: originalCompleted,
      categoryId: originalCategoryId,
    });
    setTaskStatusMessage('');
  };

  const handleCategoryEdit = (category) => {
    const originalName = getCategoryName(category);

    setCategoryName(originalName);
    setEditingCategoryId(category.id);
    setEditingCategoryOriginal({
      name: originalName,
    });
    setCategoryStatusMessage('');
  };

  const handleToggleCompleted = async (task) => {
    try {
      await axios.patch(`${API_BASE_URL}/tasks/${task.id}`, {
        ...completedPayload(!getTaskCompleted(task)),
      });
      fetchTasks();
    } catch (error) {
      console.error('Error toggling task status:', error);
      setTaskStatusMessage(`Ошибка: ${getErrorText(error)}`);
    }
  };

  const handleTaskDelete = async (id) => {
    try {
      await axios.delete(`${API_BASE_URL}/tasks/${id}`);
      if (editingTaskId === id) {
        resetTaskForm();
      }
      fetchTasks();
    } catch (error) {
      console.error('Error deleting task:', error);
      setTaskStatusMessage(`Ошибка: ${getErrorText(error)}`);
    }
  };

  const handleCategoryDelete = async (id) => {
    try {
      await axios.delete(`${API_BASE_URL}/categories/${id}`);
      if (editingCategoryId === id) {
        resetCategoryForm();
      }
      if (categoryFilter === id) {
        setCategoryFilter('all');
      }
      if (taskCategoryId === id) {
        setTaskCategoryId('');
      }
      fetchCategories();
      // у задач удалённой категории category_id должен сброситься
      fetchTasks();
    } catch (error) {
      console.error('Error deleting category:', error);
      setCategoryStatusMessage(`Ошибка: ${getErrorText(error)}`);
    }
  };

  return (
    <div className="app-shell">
      <main className="App">
        <header className="hero">
          <div className="hero-head">
            <h1>Мои задачи</h1>
            <div className="view-switcher" role="tablist" aria-label="Переключатель разделов">
              <button
                className={activeView === 'tasks' ? 'switch-btn active' : 'switch-btn'}
                onClick={() => setActiveView('tasks')}
                type="button"
              >
                Задачи
              </button>
              <button
                className={activeView === 'categories' ? 'switch-btn active' : 'switch-btn'}
                onClick={() => setActiveView('categories')}
                type="button"
              >
                Категории
              </button>
            </div>
          </div>
        </header>

        {activeView === 'tasks' ? (
          <>
            <section className="panel editor-panel">
              <div className="input-row">
                <input
                  type="text"
                  value={taskTitle}
                  onChange={(event) => setTaskTitle(event.target.value)}
                  onKeyDown={(event) => {
                    if (event.key === 'Enter') {
                      event.preventDefault();
                      handleTaskSubmit();
                    }
                  }}
                  placeholder="Введите задачу"
                />
                <button className="btn btn-primary" onClick={handleTaskSubmit} type="button">
                  {editingTaskId ? 'Сохранить' : 'Добавить'}
                </button>
              </div>

              <label className="select-row">
                <span>Категория</span>
                <select
                  value={taskCategoryId}
                  onChange={(event) => setTaskCategoryId(event.target.value)}
                >
                  <option value="">Без категории</option>
                  {categories.map((category) => (
                    <option key={category.id} value={category.id}>
                      {getCategoryName(category)}
                    </option>
                  ))}
                </select>
              </label>

              {editingTaskId && (
                <label className="checkbox-row">
                  <input
                    type="checkbox"
                    checked={isCompleted}
                    onChange={(event) => setIsCompleted(event.target.checked)}
                  />
                  Отметить как выполненную при сохранении
                </label>
              )}

              <div className="action-row">
                <button className="btn" onClick={resetTaskForm} type="button">
                  {editingTaskId ? 'Отменить редактирование' : 'Очистить поле'}
                </button>
              </div>

              {taskStatusMessage && <div className="status-message">{taskStatusMessage}</div>}
            </section>

            <section className="panel tasks-panel">
              <div className="tasks-header">
                <h2>Список задач</h2>
                <button className="btn" onClick={fetchTasks} type="button">
                  Обновить
                </button>
              </div>

              <div className="stats">
                <span className="stat-pill">Всего: {visibleTasks.length}</span>
                <span className="stat-pill">Активных: {pendingCount}</span>
                <span className="stat-pill">Готово: {completedCount}</span>
              </div>

              <label className="select-row filter-row">
                <span>Фильтр</span>
                <select
                  value={categoryFilter}
                  onChange={(event) => setCategoryFilter(event.target.value)}
                >
                  <option value="all">Все категории</option>
                  <option value="none">Без категории</option>
                  {categories.map((category) => (
                    <option key={category.id} value={category.id}>
                      {getCategoryName(category)}
                    </option>
                  ))}
                </select>
              </label>

              {visibleTasks.length === 0 ? (
                <div className="empty-state">
                  {tasks.length === 0
                    ? 'Пока пусто. Добавьте первую задачу выше.'
                    : 'В этой категории задач нет.'}
                </div>
              ) : (
                <ul>
                  {visibleTasks.map((task, index) => (
                    <li key={task.id} style={{ '--item-index': index }}>
                      <button
                        className={getTaskCompleted(task) ? 'toggle done' : 'toggle'}
                        onClick={() => handleToggleCompleted(task)}
                        aria-label="Переключить статус"
                        type="button"
                      >
                        {getTaskCompleted(task) ? '✓' : ''}
                      </button>

                      <div className="task-content">
                        <span className={getTaskCompleted(task) ? 'task-title done' : 'task-title'}>
                          {getTaskTitle(task)}
                        </span>
                        <span className="task-state">{getTaskCompleted(task) ? 'Выполнена' : 'В работе'}</span>
                        <span
                          className={
                            getTaskCategoryId(task) ? 'category-badge' : 'category-badge category-badge-empty'
                          }
                        >
                          {getTaskCategoryLabel(task, categoryNameById) || 'Без категории'}
                        </span>
                      </div>

                      <div className="task-actions">
                        <button className="btn" onClick={() => handleTaskEdit(task)} type="button">
                          Изменить
                        </button>
                        <button className="btn btn-danger" onClick={() => handleTaskDelete(task.id)} type="button">
                          Удалить
                        </button>
                      </div>
                    </li>
                  ))}
                </ul>
              )}
            </section>
          </>
        ) : (
          <>
            <section className="panel editor-panel">
              <div className="input-row">
                <input
                  type="text"
                  value={categoryName}
                  onChange={(event) => setCategoryName(event.target.value)}
                  onKeyDown={(event) => {
                    if (event.key === 'Enter') {
                      event.preventDefault();
                      handleCategorySubmit();
                    }
                  }}
                  placeholder="Введите категорию"
                />
                <button className="btn btn-primary" onClick={handleCategorySubmit} type="button">
                  {editingCategoryId ? 'Сохранить' : 'Добавить'}
                </button>
              </div>

              <div className="action-row">
                <button className="btn" onClick={resetCategoryForm} type="button">
                  {editingCategoryId ? 'Отменить редактирование' : 'Очистить поле'}
                </button>
              </div>

              {categoryStatusMessage && <div className="status-message">{categoryStatusMessage}</div>}
            </section>

            <section className="panel tasks-panel">
              <div className="tasks-header">
                <h2>Список категорий</h2>
                <button className="btn" onClick={fetchCategories} type="button">
                  Обновить
                </button>
              </div>

              <div className="stats">
                <span className="stat-pill">Всего: {categories.length}</span>
              </div>

              {categories.length === 0 ? (
                <div className="empty-state">Категорий пока нет.</div>
              ) : (
                <ul className="category-list">
                  {categories.map((category, index) => (
                    <li key={category.id} style={{ '--item-index': index }}>
                      <div className="category-mark" aria-hidden="true" />

                      <div className="task-content">
                        <span className="task-title">{getCategoryName(category)}</span>
                        <span className="task-state">{category.id}</span>
                      </div>

                      <div className="task-actions">
                        <button className="btn" onClick={() => handleCategoryEdit(category)} type="button">
                          Изменить
                        </button>
                        <button
                          className="btn btn-danger"
                          onClick={() => handleCategoryDelete(category.id)}
                          type="button"
                        >
                          Удалить
                        </button>
                      </div>
                    </li>
                  ))}
                </ul>
              )}
            </section>
          </>
        )}
      </main>
    </div>
  );
}

export default App;
