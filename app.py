from flask import Flask, request, render_template_string, url_for
import qrcode
import io
import base64
import secrets
from datetime import datetime

app = Flask(__name__)

# Demo ticket storage
tickets = {}

HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Event Pass Demo</title>

<style>
* {
    box-sizing: border-box;
}

body {
    margin: 0;
    padding: 20px;
    background: #eee9dc;
    font-family: Arial, sans-serif;
    color: #64152a;
}

.form-box {
    max-width: 650px;
    margin: 15px auto 30px;
    padding: 22px;
    background: white;
    border-radius: 12px;
}

.form-box h2 {
    margin-top: 0;
}

label {
    display: block;
    font-weight: bold;
    margin-top: 13px;
}

input, select {
    width: 100%;
    padding: 12px;
    margin-top: 6px;
    border: 1px solid #ccc;
    border-radius: 6px;
    font-size: 16px;
}

button {
    width: 100%;
    margin-top: 18px;
    padding: 14px;
    background: #70152c;
    color: white;
    border: none;
    border-radius: 7px;
    font-size: 16px;
    cursor: pointer;
}

.pass {
    width: 100%;
    max-width: 1100px;
    margin: auto;
    overflow: hidden;
    background: #fff9e9;
    border: 4px solid #d6b75b;
    border-radius: 20px;
    position: relative;
}

.header {
    min-height: 145px;
    padding: 24px;
    background: #701329;
    color: #ffe7a0;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 18px;
    border-bottom: 7px solid #e8a02d;
}

.header h1 {
