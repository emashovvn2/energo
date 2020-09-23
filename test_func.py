#!/usr/bin/env python3
import energoopros

test_string = '''[<div class="po_time">

            9 Июня 2020            с 09:00            до 9 Июня 2020            16:30
        </div>, <div class="po_time">
            16 Июня 2020            с 09:00            до 16 Июня 2020            12:00        </div>, <div class="po_time">
            16 Июня 2020            с 09:00            до 16 Июня 2020            16:30        </div>, <div class="po_time">
            19 Июня 2020            с 09:00            до 19 Июня 2020            16:30        </div>, <div class="po_time">
            23 Июня 2020            с 09:00            до 23 Июня 2020            16:30        </div>, <div class="po_time">
            29 Июня 2020            с 14:00            до 29 Июня 2020            15:00        </div>][<ul class="po_address">
<li>
                г. Томск ул. 79-й Гвардейской дивизии

                9-11,9-в,9-г,9/1,11/1,11/2,19/4            </li>
</ul>, <ul class="po_address">
<li>
                Томск ул. 79-й Гвардейской дивизии

                6            </li>
</ul>, <ul class="po_address">
<li>
                г. Томск ул. 79-й Гвардейской дивизии

                25,25-а,25/1,25/2            </li>
</ul>, <ul class="po_address">
<li>
                г. Томск ул. 79-й Гвардейской дивизии

                29-31,31/1            </li>
</ul>, <ul class="po_address">
<li>
                г. Томск 79-й Гвардейской дивизии ул

                4,4/1,4/2,4/4,4/5,4/6,4/7,4/8            </li>
</ul>, <ul class="po_address">
<li>
                г. Томск ул. 79-й Гвардейской дивизии

                9-в,9-г,13,13-б,13/1,13/2            </li>
</ul>]'''




def test_one_digit_pass():
    assert energoopros.find_home(test_string, '4') == True

def test_one_digit_reject():
    assert energoopros.find_home(test_string, '444') == False

def test_drob_pass():
    assert energoopros.find_home(test_string, '25/1') == True

def test_drob_reject():
    assert energoopros.find_home(test_string, '4/99') == False

def test_interval_pass():
    assert energoopros.find_home(test_string, '30') == True

def test_interval_reject():
    assert energoopros.find_home(test_string, '60') == False

def test_digit_word_pass():
    assert energoopros.find_home(test_string, '9-г') == True

def test_digit_word_reject():
    assert energoopros.find_home(test_string, '9-р') == False

def test_abrakadabra_1_reject():
    assert energoopros.find_home(test_string, 'sadfwa') == False

def test_abrakadabra_2_reject():
    assert energoopros.find_home(test_string, '30sadfwa') == False

def test_abrakadabra_3_reject():
    assert energoopros.find_home(test_string, 'sadfwa9') == False

#print(energoopros.find_home(test_string, '4/99'))
