document.addEventListener("DOMContentLoaded", () => {

    // ⬇ alternar abas
    document.querySelectorAll(".perfil-tab").forEach(btn => {
        btn.addEventListener("click", () => {
            document.querySelector(".perfil-tab.active")?.classList.remove("active");
            btn.classList.add("active");

            document.querySelector(".tab-content.active")?.classList.remove("active");
            document.getElementById(btn.dataset.tab).classList.add("active");
        });
    });

    // ⬇ buscar dados do perfil
    fetch("/api/perfil")
        .then(res => res.json())
        .then(data => {
            // visão geral
            document.getElementById("total-compras").textContent = data.total_compras;
            document.getElementById("total-favoritos").textContent = data.favoritos.length;

            // favoritos
            let favDiv = document.getElementById("listaFavoritos");
            data.favoritos.forEach(f => {
                favDiv.innerHTML += `
                    <div class="fav-item">
                        <img src="${f.imagem}">
                        <p>${f.nome}</p>
                    </div>
                `;
            });

            // compras
            let tabela = document.getElementById("tabelaCompras");
            data.compras.forEach(c => {
                tabela.innerHTML += `
                    <tr>
                        <td>${c.data}</td>
                        <td>${c.produto}</td>
                        <td>${c.quantidade}</td>
                        <td>R$ ${c.valor}</td>
                    </tr>
                `;
            });

            // gráfico
            new Chart(document.getElementById("chartCompras"), {
                type: "bar",
                data: {
                    labels: data.estatisticas.meses,
                    datasets: [{
                        label: "Compras por Mês",
                        data: data.estatisticas.valores
                    }]
                }
            });

        });

});
