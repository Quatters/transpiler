const API_URL = '/'

const mirrorConfig = {
    lineNumbers: true,
    lineWrapping: true,
}

function restoreData() {
    const sourcecode = window.localStorage.getItem('sourcecode') || '';
    const destcode = window.localStorage.getItem('destcode') || '';
    const canDownload = window.localStorage.getItem('canDownload') || false;
    sourceCm.setValue(sourcecode);
    destCm.setValue(destcode);
    buttonDownload.toggleAttribute('disabled', !canDownload);
    fileInput.value = '';
}

function download(filename, text) {
    const element = document.createElement('a');
    element.setAttribute('href', 'data:text/plain;charset=utf-8,' + encodeURIComponent(text));
    element.setAttribute('download', filename);
    element.style.display = 'none';
    document.body.appendChild(element);
    element.click();
    document.body.removeChild(element);
  }

const debounce = (callback, wait = 300) => {
    let timeoutId = null;
    return (...args) => {
        clearTimeout(timeoutId);
        timeoutId = setTimeout(() => {
            callback.apply(null, args);
        }, wait);
    };
}

const buttonClear = document.querySelector('#button-clear');
const buttonTranspile = document.querySelector('#button-transpile');
const fileInput = document.querySelector('#file-input');
const statusLine = document.querySelector('#status-line');
const buttonDownload = document.querySelector('#button-download');

const sourceCm = CodeMirror.fromTextArea(
    document.querySelector('textarea#sourcecode'),
    mirrorConfig,
);
const destCm = CodeMirror.fromTextArea(
    document.querySelector('textarea#destcode'),
    {
        ...mirrorConfig,
        readOnly: true,
    }
);

const saveSourcecode = debounce(() => {
    window.localStorage.setItem('sourcecode', sourceCm.getValue());
    statusLine.innerHTML = `Saved from ${new Date().toLocaleTimeString()}`;
});

sourceCm.on('change', saveSourcecode);

buttonClear.addEventListener('click', function () {
    fileInput.value = '';
    sourceCm.setValue('');
    destCm.setValue('');
    window.localStorage.setItem('destcode', '');
    window.localStorage.setItem('sourcecode', '');
});

buttonTranspile.addEventListener('click', async function () {
    const sourcecode = sourceCm.getValue();
    response = await fetch('/transpile', {
        method: 'POST',
        mode: 'same-origin',
        credentials: 'same-origin',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            code: sourcecode,
        })
    });
    const responseJson = await response.json();
    const result = responseJson.result;
    destCm.setValue(result);

    const canDownload = responseJson.success;
    buttonDownload.toggleAttribute('disabled', !responseJson.success);

    window.localStorage.setItem('sourcecode', sourcecode);
    window.localStorage.setItem('destcode', result);
    window.localStorage.setItem('canDownload', canDownload);
})

fileInput.addEventListener('change', function () {
    const file = this.files[0];
    reader = new FileReader();
    reader.readAsText(file);
    reader.onload = function () {
        sourceCm.setValue(reader.result);
        window.localStorage.setItem('sourcecode', reader.result);
    }
});

buttonDownload.addEventListener('click', function () {
    download('pascal-to-csharp.cs', destCm.getValue());
});

restoreData();
