document.addEventListener('DOMContentLoaded', function() {
    const agregarCategoriaBtn = document.getElementById('agregar_categoria');
    const categoriasInput = document.getElementById('categorias_input');

    agregarCategoriaBtn.addEventListener('click', function() {
        const nuevaCategoriaHTML = `
            <div class="categoria">
                <label for="categoria_${categoriasInput.children.length + 1}">Categoría ${categoriasInput.children.length + 1}:</label>
                <input type="text" id="categoria_${categoriasInput.children.length + 1}" name="categoria_${categoriasInput.children.length + 1}" required>
                <label for="cantidad_qr_${categoriasInput.children.length + 1}">Cantidad de códigos QR:</label>
                <input type="number" id="cantidad_qr_${categoriasInput.children.length + 1}" name="cantidad_qr_${categoriasInput.children.length + 1}" required>
            </div>
        `;
        categoriasInput.insertAdjacentHTML('beforeend', nuevaCategoriaHTML);
    });
});
