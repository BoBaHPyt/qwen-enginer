from lxml import etree

# Пример XML с элементами <code> и <code-replace>
xml_content = """
<root>
    <code>
        Текст перед заменой
        <code-replace>Замена</code-replace>
        Текст после замены
        <html>Hello
  </html>
    </code>
</root>
"""

# Парсим XML
root = etree.fromstring(xml_content)

# Находим все элементы <code>
for code in root.xpath('//code'):
    # Создаем новый список для хранения элементов <code-replace>
    code_replace_elements = []
    # Собираем текст, исключая содержимое <code-replace>
    cdata_text = []
    
    # Проходим по всем дочерним элементам внутри <code>
    for child in code:
        if child.tag == 'code-replace':
            # Если элемент является <code-replace>, добавляем его в отдельный список
            code_replace_elements.append(child)
        else:
            cdata_text.append(etree.tostring(child).decode())
        
        # Добавляем текст после элемента (tail)
        if child.tail.strip():
            cdata_text.append(child.tail.strip())
            child.tail = ""
    
    # Если начальный текст есть, добавляем его
    if code.text:
        cdata_text.insert(0, code.text.strip())
    
    # Объединяем все собранные тексты в один строковый объект
    cdata_text = '\n'.join(cdata_text)
    
    # Удаляем все дочерние элементы из текущего <code>
    code.clear()
    
    
    # Добавляем собранный текст в CDATA
    if cdata_text:
        cdata = etree.CDATA(cdata_text)
        code.text = cdata
    
    # Добавляем обратно сохраненные элементы <code-replace>
    for child in code_replace_elements:
        code.append(child)

# Выводим результат
print(etree.tostring(root, pretty_print=True, encoding='unicode'))
