API_URL = '/'

const sourceCm = CodeMirror.fromTextArea(
    document.querySelector('textarea#sourcecode'),
    {
        lineNumbers: true,
    }
);
const destCm = CodeMirror.fromTextArea(
    document.querySelector('textarea#destcode'),
    {
        lineNumbers: true,
        readOnly: true,
    }
);


async function send() {
    const sourcecode = sourceCm.getValue().trim();
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
    destCm.setValue(responseJson.result);
}
