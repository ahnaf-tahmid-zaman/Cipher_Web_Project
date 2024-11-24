document.getElementById('cipherForm').addEventListener('submit', function (e) {
    e.preventDefault();

    const cipherType = document.getElementById('cipherType').value;
    const operation = document.getElementById('operation').value;
    const text = document.getElementById('text').value;
    const key = document.getElementById('key').value;

    fetch('/cipher', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            cipher_type: cipherType,
            operation: operation,
            text: text,
            key: key
        })
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById('result').textContent = `Result: ${data.result}`;
    })
    .catch(error => console.error('Error:', error));
});
