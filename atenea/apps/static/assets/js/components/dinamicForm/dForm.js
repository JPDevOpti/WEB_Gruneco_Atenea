document.addEventListener('DOMContentLoaded', function () {
    // Estado para controlar los formularios abiertos
    const formulariosAbiertos = new Set();

    // Referencias al contenedor y botón
    const contenedorFormularios = document.getElementById('formulario-dinamicos');
    const botonAgregarFormulario = document.getElementById('agregar-formulario');

    // Manejar el clic en el botón para agregar un formulario dinámico
    botonAgregarFormulario.addEventListener('click', async function () {
        const formType = 'form-dinamico'; // Ajustar según el identificador necesario
        if (formulariosAbiertos.has(formType)) {
            Swal.fire({
                title: 'Formulario ya abierto',
                text: 'Este formulario ya está cargado.',
                icon: 'warning',
            });
            return;
        }

        try {
            // Cargar el HTML del formulario desde la vista de Django
            const response = await fetch(`/registro_demografico/`);
            if (response.ok) {
                const formHtml = await response.text();

                // Crear un contenedor para el formulario
                const container = document.createElement('div');
                container.id = `container-${formType}`;
                container.innerHTML = formHtml;

                // Agregar el formulario al contenedor principal
                contenedorFormularios.appendChild(container);

                // Añadir al estado de formularios abiertos
                formulariosAbiertos.add(formType);

                // Inicializar el formulario
                initializeForm(formType);
            } else {
                throw new Error('No se pudo cargar el formulario');
            }
        } catch (error) {
            console.error('Error al cargar el formulario:', error);
            Swal.fire({
                title: 'Error',
                text: 'No se pudo cargar el formulario',
                icon: 'error',
            });
        }
    });

    // Función para inicializar eventos en un formulario específico
    function initializeForm(formType) {
        const form = document.querySelector(`#form-${formType}`);
        if (!form) return;
    }

    // Función para cerrar un formulario dinámico desde el botón Cancelar
    window.cerrarFormulario = function (button) {
        const container = button.closest('div[id^="container-"]');

        if (container) {
            const formType = container.id.replace('container-', '');
            container.remove();
            formulariosAbiertos.delete(formType);
        }
    };

    // Función para obtener el token CSRF
    function getCookie(name) {
        const cookieValue = document.cookie
            .split('; ')
            .find(row => row.startsWith(name + '='))?.split('=')[1];
        return cookieValue || '';
    }
});
