# Deployment Fix - AVIF Support

## Проблема
Production deployment упал из-за отсутствия поддержки AVIF в Docker контейнере.

## Решение

### 1. Обновлен Dockerfile
Добавлены системные библиотеки для AVIF:
- **Build stage**: `libavif-dev` (для компиляции)
- **Runtime stage**: `libavif15` (для работы приложения)

### 2. Убран pillow-avif-plugin
Pillow 12.1.1 имеет встроенную поддержку AVIF при наличии системной библиотеки.
Плагин не нужен и был удален из requirements.txt.

### 3. Добавлен fallback на WebP
Если AVIF недоступен (старая система, отсутствие библиотеки), автоматически используется WebP:

```python
try:
    img.save(output_path, 'AVIF', quality=85, speed=6)
except (KeyError, OSError, ValueError) as e:
    logger.warning(f"AVIF encoding failed, falling back to WebP: {e}")
    actual_path = output_path.with_suffix('.webp')
    img.save(actual_path, 'WEBP', quality=85, method=6)
```

### 4. Обновлена логика возврата путей
`create_thumbnail()` теперь возвращает `(size, actual_path)`, чтобы использовать правильное расширение файла.

## Тестирование

```bash
# Локально проверить что все работает
cd backend
python -m py_compile routers/upload.py
python -c "from routers.upload import create_thumbnail; print('OK')"
```

## Деплой

После коммита изменений, GitHub Actions должен успешно задеплоить:
1. Docker соберет образ с libavif15
2. Pillow сможет создавать AVIF изображения
3. Если что-то пойдет не так - fallback на WebP

## Файлы изменены
- `backend/Dockerfile` - добавлены AVIF библиотеки
- `backend/requirements.txt` - убран pillow-avif-plugin
- `backend/routers/upload.py` - добавлен fallback и обновлена логика
- `BUGFIXES.md` - обновлена документация
