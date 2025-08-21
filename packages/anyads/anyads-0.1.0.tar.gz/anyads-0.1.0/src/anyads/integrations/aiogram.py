# src/anyads/integrations/aiogram.py

try:
    from aiogram import Dispatcher, types
    from anyads.client import _sdk_instance
except ImportError:
    pass 

def register_anyads_handlers(dp: 'Dispatcher'):
    """
    Функция-хелпер для автоматической регистрации обработчика
    верификационной команды в aiogram.
    
    Для использования установите SDK с поддержкой aiogram:
    pip install anyads[aiogram]
    """
    if _sdk_instance is None:
        raise RuntimeError("AnyAds SDK не инициализирован. Вызовите anyads.init() перед регистрацией обработчиков.")

    @dp.message(lambda msg: msg.text and msg.text.startswith('/verify_anyads_'))
    async def _handle_verification_command(message: types.Message):
        success = await _sdk_instance.process_verification_code(message.text)
        
        if success:
            await message.answer("✅ Верификация SDK AnyAds успешно пройдена!")
        else:
            await message.answer("❌ Произошла ошибка во время верификации. Попробуйте снова или обратитесь в поддержку.")