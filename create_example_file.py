#!/usr/bin/env python3
"""
Скрипт для создания примера Excel-файла для планировщика расписания.

Для работы скрипта необходимо установить зависимости:
    pip install pandas openpyxl
"""
try:
    import pandas as pd
    from datetime import datetime
    
    # Создаем Excel-файл с несколькими листами
    with pd.ExcelWriter('example_schedule.xlsx', engine='openpyxl') as writer:
        
        # Лист "Упражнения"
        exercises = pd.DataFrame({
            'Название': ['Индивидуальная', 'Командная', 'Парная'],
            'Длительность': [15, 30, 20]
        })
        exercises.to_excel(writer, sheet_name='Упражнения', index=False)
        
        # Лист "Этапы"
        stages = pd.DataFrame({
            'МаксимумУчастников': [5, 10, 15, 20]
        })
        stages.to_excel(writer, sheet_name='Этапы', index=False)
        
        # Лист "Корты"
        courts = pd.DataFrame({
            'Корт': ['Зал 1', 'Зал 1', 'Зал 2', 'Зал 3'],
            'Открытие': ['09:00:00', '14:00:00', '09:00:00', '10:00:00'],
            'Закрытие': ['13:00:00', '18:00:00', '18:00:00', '17:00:00']
        })
        courts.to_excel(writer, sheet_name='Корты', index=False)
        
        # Лист "Группы"
        groups = pd.DataFrame({
            'ИмяГруппы': ['Группа А', 'Группа Б', 'Группа В', 'Группа Г'],
            'КоличествоУчастников': [10, 15, 8, 12],
            'Упражнение': ['Индивидуальная', 'Командная', 'Индивидуальная', 'Парная'],
            'МинимальноеВремяНачала': [540, None, 600, None],  # 540 = 09:00, 600 = 10:00
            'МаксимальноеВремяОкончания': [1080, 1200, None, 1020]  # 1080 = 18:00, 1200 = 20:00, 1020 = 17:00
        })
        groups.to_excel(writer, sheet_name='Группы', index=False)
    
    print("✅ Файл example_schedule.xlsx успешно создан!")
    print("\nСтруктура файла:")
    print("  - Лист 'Упражнения': 3 упражнения")
    print("  - Лист 'Этапы': 4 этапа")
    print("  - Лист 'Корты': 3 корта (Зал 1 с перерывом)")
    print("  - Лист 'Группы': 4 группы")
    
except ImportError:
    print("❌ Ошибка: не установлены необходимые библиотеки")
    print("\nУстановите зависимости:")
    print("  pip install pandas openpyxl")
    print("\nИли создайте файл вручную, следуя инструкции в файле ИНСТРУКЦИЯ_ПО_РАБОТЕ_С_ФАЙЛОМ.md")
except Exception as e:
    print(f"❌ Ошибка при создании файла: {e}")
