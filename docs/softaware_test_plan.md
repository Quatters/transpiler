## <center>План по тестированию продукта</center>
<br>
<center><i>Транслятор из Pascal в C#</i></center>
<br>

### **История изменений документа**

| **Дата**   | **Автор**     | **Внесенные изменения**                                                     |
|------------|---------------|-----------------------------------------------------------------------------|
| 19.12.2022 | А.А. Аликаева | Исходная версия тестов                                                      |

### **Тесты для тестирования подсистемы «Пользовательский интерфейс»**

<u>Тест TEST_UI_001</u>  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Тестируемые требования: REQ_UI_001  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Описание теста: Нажать на окно ввода, начать вводить любой текст с клавиатуры  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Ожидаемый результат: Печатаемый текст отображается в окне ввода  

<u>Тест TEST_UI_002</u>  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Тестируемые требования: REQ_UI_001  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Описание теста: Нажать на окно вывода, начать вводить любой текст с клавиатуры  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Ожидаемый результат: Печатаемый текст не отображается в окне вывода  

<u>Тест TEST_UI_003</u>  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Тестируемые требования: REQ_UI_001, REQ_UI_002, REQ_UI_005, REQ_SYNA_001    
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Описание теста: Нажать на окно ввода, ввести ```test```, нажать на кнопку «Transpile»  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Ожидаемый результат: В окне вывода отобразилось сообщение об ошибке вида ```SyntaxError: test at line 1. Expected '  START  '```  

<u>Тест TEST_UI_004</u>  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Тестируемые требования: REQ_UI_001, REQ_UI_003   
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Описание теста: Нажать на копку «Выберите файл», выбрать любой файл формата «.txt» или «.pas»  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Ожидаемый результат: В окне ввода отобразилось содержимое выбранного файла, справа от кнопки «Выберите файл» написано название файла  

<u>Тест TEST_UI_005</u>  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Тестируемые требования: REQ_UI_001, REQ_UI_006   
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Описание теста: Нажать на окно ввода, ввести ```test```, нажать на кнопку «Clear»  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Ожидаемый результат: Окно ввода очищено   

### **Тесты для тестирования подсистемы «Лексический анализатор»**

<u>Тест TEST_LA_001</u>  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Тестируемые требования: REQ_LA_001, REQ_UI_001, REQ_UI_002, REQ_UI_004, REQ_UI_005       
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Описание теста:  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;1. Нажать на окно ввода  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;2. Ввести  
```
begin
{
var4: string := 'some string1';
end.
```
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;3. Нажать на кнопку «Transpile»  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Ожидаемый результат:  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;1. Окно вывода содержит сообщение о лексической ошибке вида ```UnexpectedTokenError: { at line 2```  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;2. Кнопка «Download» недоступна для нажатия  

<u>Тест TEST_LA_002</u>  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Тестируемые требования: REQ_LA_001, REQ_SYNA_001, REQ_SEMA_001, REQ_CG_001, REQ_UI_001, REQ_UI_004, REQ_UI_005   
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Описание теста:  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;1. Нажать на окно ввода  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;2. Ввести  
```
begin
println('Hello, World');
end.
```
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;3. Нажать на кнопку «Transpile»  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Ожидаемый результат:   
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;1. Окно вывода содержит код на языке C#  
```
using System;

namespace Transpiler
{
    internal class Program
    {

        public static void Main(string[] args)
        {
            Console.WriteLine("Hello, World");
        }

    }
}
```
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;2. Кнопка «Download» доступна для нажатия  

### **Тесты для тестирования подсистемы «Синтаксический анализатор»**

<u>Тест TEST_SYNA_001</u>  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Тестируемые требования: REQ_LA_001, REQ_SYNA_001, REQ_UI_001, REQ_UI_002, REQ_UI_004, REQ_UI_005    
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Описание теста:  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;1. Нажать на окно ввода  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;2. Ввести  
```
beg$in
end.
```
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;3. Нажать на кнопку «Transpile»  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Ожидаемый результат:  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;1. Окно вывода содержит сообщение о синтаксической ошибке вида ```SyntaxError: beg at line 1. Expected '  START  '```  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;2. Кнопка «Download» недоступна для нажатия

<u>Тест TEST_SYNA_002</u>  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Тестируемые требования: REQ_LA_001, REQ_SYNA_001, REQ_UI_001, REQ_UI_002, REQ_UI_004, REQ_UI_005    
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Описание теста:  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;1. Нажать на окно ввода  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;2. Ввести  
```
begin
println('Hello, World')
end.
```
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;3. Нажать на кнопку «Transpile»  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Ожидаемый результат:  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;1. Окно вывода содержит сообщение о синтаксической ошибке вида ```SyntaxError: end at line 3. Expected 'semicolon'```  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;2. Кнопка «Download» недоступна для нажатия

<u>Тест TEST_SYNA_003</u>  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Тестируемые требования: REQ_LA_001, REQ_SYNA_001, REQ_SEMA_001, REQ_CG_001, REQ_UI_001, REQ_UI_004, REQ_UI_005    
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Описание теста:  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;1. Нажать на окно ввода  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;2. Ввести  
```
var test: boolean := true;
begin
if (2 < 5) or (test) then
begin
    test := false;
end;
end.
```
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;3. Нажать на кнопку «Transpile»  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Ожидаемый результат:  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;1. Окно вывода содержит код на языке C#  
```
using System;

namespace Transpiler
{
    internal class Program
    {
        static bool test = true;

        public static void Main(string[] args)
        {
            if ((2 < 5) || (test))
            {
                test = false;
            }
        }

    }
}
```
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;2. Кнопка «Download» доступна для нажатия

### **Тесты для тестирования подсистемы «Семантический анализатор»**

<u>Тест TEST_SEMA_001</u>  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Тестируемые требования: REQ_LA_001, REQ_SYNA_001, REQ_SEMA_001, REQ_UI_001, REQ_UI_002, REQ_UI_004, REQ_UI_005    
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Описание теста:  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;1. Нажать на окно ввода  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;2. Ввести  
```
var test: boolean := true;
begin
test := 2;
end.
```
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;3. Нажать на кнопку «Transpile»  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Ожидаемый результат:  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;1. Окно вывода содержит сообщение о семантической ошибке вида ```SemanticError: 2 at line 3 - expression is not compatible with type boolean```  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;2. Кнопка «Download» недоступна для нажатия

<u>Тест TEST_SEMA_002</u>  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Тестируемые требования: REQ_LA_001, REQ_SYNA_001, REQ_SEMA_001, REQ_UI_001, REQ_UI_002, REQ_UI_004, REQ_UI_005    
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Описание теста:  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;1. Нажать на окно ввода  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;2. Ввести  
```
begin
var a: integer := 15;
var a: integer;
end.
```
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;3. Нажать на кнопку «Transpile»  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Ожидаемый результат:  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;1. Окно вывода содержит сообщение о семантической ошибке вида ```SemanticError: a at line 3 - variable is already defined```  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;2. Кнопка «Download» недоступна для нажатия

### **Тесты для тестирования подсистемы «Генератор кода»**

<u>Тест TEST_CG_001</u>  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Тестируемые требования: REQ_LA_001, REQ_SYNA_001, REQ_SEMA_001, REQ_CG_001, REQ_UI_001, REQ_UI_004, REQ_UI_005    
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Описание теста:  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;1. Нажать на окно ввода  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;2. Ввести  
```
var a: real := 2.0;
begin
var b: real := a * a;
println(b);
end.
```
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;3. Нажать на кнопку «Transpile»  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Ожидаемый результат:  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;1. Окно вывода содержит код на языке C#  
```
using System;

namespace Transpiler
{
    internal class Program
    {
        static double a = 2.0;

        public static void Main(string[] args)
        {
            double b = a * a;
            Console.WriteLine(b);
        }

    }
}
```
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;2. Кнопка «Download» доступна для нажатия

### **Тесты для тестирования системы в целом (System Test)**

<u>Тест TEST_SYS_001</u>  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Тестируемые требования: REQ_LA_001, REQ_SYNA_001, REQ_SEMA_001, REQ_CG_001, REQ_UI_001, REQ_UI_004, REQ_UI_005, REQ_UI_006    
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Описание теста:  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;1. Нажать на окно ввода  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;2. Ввести  
```
begin
println('Hello, World');
end.
```
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;3. Нажать на кнопку «Transpile»  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;4. Нажать на кнопку «Download» и сохранить файл  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;5. Нажать на кнопку «Clear»  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Ожидаемый результат:  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;1. Окно вывода содержит код на языке C#  
```
using System;

namespace Transpiler
{
    internal class Program
    {

        public static void Main(string[] args)
        {
            Console.WriteLine("Hello, World");
        }

    }
}
```  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;2. Файл сохранен на устройство  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;3. После нажатия на кнопку «Clear» будет очищено окно ввода и вывода  

<u>Тест TEST_SYS_002</u>  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Тестируемые требования: REQ_LA_001, REQ_SYNA_001, REQ_SEMA_001, REQ_CG_001, REQ_UI_001, REQ_UI_003, REQ_UI_005, REQ_UI_006    
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Описание теста:  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;1. Нажать на кнопку «Выберите файл» и выбрать файл формата «.txt» или «.pas»   
```
// условное содержание файла
begin
println('Hello, World');
end.
```
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;2. Нажать на кнопку «Transpile»   
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;3. Нажать на кнопку «Clear»  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Ожидаемый результат:  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;1. После выбора файла окно ввода содержит код на языке Pascal и рядом с кнопкой «Выберите файл» отображено название выбранного файла  
```
// условное содержание файла
begin
println('Hello, World');
end.
```
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;2. Окно вывода содержит код на языке C#  
```
using System;

namespace Transpiler
{
    internal class Program
    {

        public static void Main(string[] args)
        {
            Console.WriteLine("Hello, World");
        }

    }
}
```
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;3. После нажатия на кнопку «Clear» будет очищено окно ввода, окно вывода и строка, содержащее название выбранного файла

<u>Тест TEST_SYS_003</u>  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Тестируемые требования: REQ_LA_001, REQ_SYNA_001, REQ_SEMA_001, REQ_UI_001, REQ_UI_002, REQ_UI_004, REQ_UI_005    
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Описание теста:  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;1. Нажать на окно ввода  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;2. Ввести  
```
begin
var a: integer := 15;
var a: integer;
end.
```
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;3. Нажать на кнопку «Transpile»  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;4. Нажать на кнопку «Download» и сохранить файл  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Ожидаемый результат:  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;1. Окно вывода содержит сообщение о семантической ошибке вида ```SemanticError: a at line 3 - variable is already defined```  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;2. Кнопка «Download» недоступна для нажатия