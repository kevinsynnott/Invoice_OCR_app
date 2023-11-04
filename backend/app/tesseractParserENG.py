import re
import requests
import os

backend_hostname = os.environ.get("BACKEND_HOSTNAME", "localhost")
backend_port = os.environ.get("BACKEND_PORT", "5000")

def get_invoice_number(lines):
    invoice_number = ''
    after_word = False
    pattern = re.compile(r'\d+')
    for line in lines:
        if any([kw in line.lower() for kw in ('invoice', 'invoice:', 'invoices')]):
            words = line.split()
            for word in words:
                if any([kw in word.lower() for kw in ('invoice', 'invoice:', 'invoices')]):
                    after_word = True
                if word.isdigit() and after_word:
                    invoice_number = word
                    return invoice_number
                else:
                    match = pattern.search(word)
                    if match and after_word:
                        invoice_number = match.group()
                        return invoice_number
    return invoice_number

def get_variable_symbol(lines):
    var_symbol = ''
    for line in lines:
        if any([kw in line.lower() for kw in ('variable', 'var.symbol', 'vs:', 'v.s.', 'variable:')]):
            words = line.split()
            for word in words:
                if word.isdigit():
                    var_symbol = word
                    return var_symbol
    return var_symbol

def get_date_of_issue(lines):
    date_of_issue = ''
    date_pattern = re.compile(r"\d{1,2}\s*[-.:]\s*\d{1,2}\s*[-.:]\s*\d{2,4}")
    for line in lines:
        if 'date' in line.lower():
            if 'issued' in line.lower():
                match = date_pattern.search(line)
            if match:
                date_of_issue = match.group()
                return date_of_issue
        if any([kw in line.lower() for kw in ('date of issue', 'date of issuance', 'date of issuance:', 'issued:', 'issuance:', 'issued')]):
            match = date_pattern.search(line)
            if match:
                date_of_issue = match.group()
                return date_of_issue
    return date_of_issue

def get_due_date(lines):
    due_date = ''
    date_pattern = re.compile(r"\d{1,2}\s*[-.:]\s*\d{1,2}\s*[-.:]\s*\d{2,4}")
    for line in lines:
        if any([kw in line.lower() for kw in ('due date', 'due', 'due date:', 'due dates:', 'duedates')]):
            match = date_pattern.search(line)
            if match:
                due_date = match.group()
                return due_date
    return due_date

def get_delivery_date(lines):
    delivery_date = ''
    date_pattern = re.compile(r"\d{1,2}\s*[-.:]\s*\d{1,2}\s*[-.:]\s*\d{2,4}")
    for line in lines:
        if any([kw in line.lower() for kw in ('delivery date', 'delivery date:', 'date of delivery', 'delivery', 'delivery date:', 'tax obligation')]):
            match = date_pattern.search(line)
            if match:
                delivery_date = match.group()
                return delivery_date
    return delivery_date

def get_payment_method(lines):
    payment_method = ''
    for line in lines:
        if any([kw in line.lower() for kw in ('payment method', 'payment method:', 'payment form', 'payment method:', 'payment method', 'payment')]):
            words = line.split()
            for i, word in enumerate(words):
                if word.lower().rstrip('.:') == 'payment' or word.lower().rstrip('.:') == 'payment' or word.lower().rstrip('.:') == 'payment' or word.lower().rstrip('.:') == 'payment':
                    if any(x in words for x in ['bank transfer', 'Bank Transfer', 'by bank transfer', 'By Bank Transfer']):
                        payment_method = 'Bank Transfer'
                    elif any(x in words for x in ['cash', 'Cash', 'in cash', 'In Cash', 'cash']):
                        payment_method = 'In Cash'
                    elif any(x in words for x in ['cash on delivery', 'Cash on Delivery', 'by cash on delivery', 'By Cash on Delivery']):
                        payment_method = 'Cash on Delivery'
                    elif ':PP' in words:
                        payment_method = 'PP'
                    else:
                        if i+1 < len(words) and words[i + 1].isalpha():
                            payment_method = words[i + 1]
                        elif i+2 < len(words):
                            payment_method = words[i + 2]
                    return payment_method
    return payment_method

def get_total_price(lines):
    total_price = ''
    pattern = re.compile(r"€?\b\d+(?:[,\s]\d+)*\b")
    for line in lines:
        if any([kw1 in line.lower() and kw2 in line.lower() for kw1, kw2 in (('total', '€'), ('together', '€'), ('total', 'eur'), ('together', 'eur'),
                                                                         ('total amount', '€'), ('billed amount', '€'), (
                                                                             'total value', 'amount'), ('sum', ' payment:'),
                                                                         ('together', 'payment'), ('billed', 'amount'), (
                                                                             'total', 'payment'),
                                                                         ('to', 'pay'))]):
            line = re.sub(r'(\d)\s+(\d)', r'\1\2', line)
            words = line.split()
            for word in words:
                if pattern.match(word):
                    total_price = word
                    return total_price
    return total_price

def get_bank(lines):
    bank = ''
    for line in lines:
        if 'general' in line.lower() or 'vub' in line.lower():
            bank = 'General Credit Bank'
            return bank
        if 'csob' in line.lower() or 'czechoslovak commercial' in line.lower():
            bank = 'CSOB'
            return bank
        if 'tatrabank' in line.lower() or 'tatra' in line.lower():
            bank = 'Tatrabank'
            return bank
        if 'bank' in line.lower():
            words = line.split()
            last_word_index = len(words) - 1
            for i, word in enumerate(words):
                if word.lower() == 'bank:' and i != last_word_index:
                    bank = words[i + 1]
                    return bank
    return bank

def get_swift(lines):
    swift = ''
    pattern = re.compile(r'^[A-Z]{6}[A-Z0-9]{2}([A-Z0-9]{3})?$')
    for line in lines:
        if any([kw in line.lower() for kw in ('swift', 'swft', 'swiet', 'bic')]):
            words = line.split()
            for word in words:
                if len(word) >= 8:
                    if pattern.match(word):
                        swift = word
                        return swift
                    elif 'swift:' in word.lower():
                        possible_swift = word.split(':')[1]
                        if pattern.match(possible_swift):
                            swift = possible_swift
                            return swift
            for i, word in enumerate(words):
                last_word_index = len(words) - 1
                if word.lower() == 'swift:' and i != last_word_index:
                    swift = words[i + 1]
                    return swift
    return swift

def get_iban(lines):
    iban = ''
    pattern = re.compile(
        r'[a-zA-Z]{2}\s*[0-9]{2}[a-zA-Z0-9]{4}[0-9]{7}([a-zA-Z0-9]?){0,16}')
    for line in lines:
        if 'iban' in line.lower() or 'account'.rstrip(':') in line.lower():
            line = re.sub(r'(\d)\s+(\d)', r'\1\2', line)
            match = pattern.search(line)
            if match:
                iban = match.group()
                return iban
    return iban

def get_supplier_ico(lines):
    ico = ''
    pattern = re.compile(r"\b\d{8}\b")
    for i, line in enumerate(lines):
        keywords = ('ico', '1ico:', '1ico', 'ic:', '10', 'icq')
        count = sum([line.lower().count(kw) for kw in keywords])
        if count >= 2 or (count == 1 and 'buyer' not in line.lower()):
            words = line.split()
            for j, word in enumerate(words):
                if pattern.match(word):
                    ico = word.rstrip(',')
                    del word
                    del words[j]
                    lines[i] = ' '.join(words)
                    return ico
    return ico

def get_buyer_ico(lines):
    ico = ''
    pattern = re.compile(r"\b\d{8}\b")
    for i, line in enumerate(lines):
        if any([kw in line.lower() for kw in ('ico', '1ico:', '1ico', 'ic:', '10', 'icq')]):
            words = line.split()
            for j, word in enumerate(words):
                if pattern.match(word):
                    ico = word
                    del word
                    del words[j]
                    lines[i] = ' '.join(words)
                    return ico
                if ':' in word:
                    possible_ico = word.split(':')[1]
                    if pattern.match(possible_ico):
                        ico = possible_ico
                        return ico
    return ico

def parse_text_ENG(text):
    lines = text.split('\n')
    supplier_data = {}
    buyer_data = {}

    supplier_ico = get_supplier_ico(lines)
    if supplier_ico:
        details_url = f"http://{backend_hostname}:{backend_port}/get_details?ico={supplier_ico}"
        supplier_details = requests.post(details_url)

        if supplier_details.status_code == 200:
            supplier_data = supplier_details.json()['data']

    buyer_ico = get_buyer_ico(lines)
    if buyer_ico:
        details_url = f"http://{backend_hostname}:{backend_port}/get_details?ico={buyer_ico}"
        buyer_details = requests.post(details_url)

        if buyer_details.status_code == 200:
            buyer_data = buyer_details.json()['data']

    data = {
        'invoice_number': get_invoice_number(lines),
        'var_symbol': get_variable_symbol(lines),
        'date_of_issue': get_date_of_issue(lines),
        'due_date': get_due_date(lines),
        'delivery_date': get_delivery_date(lines),
        'payment_method': get_payment_method(lines),
        'total_price': get_total_price(lines),
        'bank': get_bank(lines),
        'swift': get_swift(lines),
        'iban': get_iban(lines),
        'buyer_ico': buyer_ico,
        'supplier_ico': supplier_ico,
        'supplier_data': supplier_data,
        'buyer_data': buyer_data
    }
    return data
