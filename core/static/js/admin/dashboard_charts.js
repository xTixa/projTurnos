document.addEventListener("DOMContentLoaded", function () {
    // Gráfico de Alunos por UC
    const chartAlunosCanvas = document.getElementById("chartAlunos");
    if (chartAlunosCanvas && window.chartAlunosData) {
        new Chart(chartAlunosCanvas, {
            type: "bar",
            data: {
                labels: window.chartAlunosData.labels,
                datasets: [{
                    label: "Alunos Inscritos",
                    data: window.chartAlunosData.values,
                    backgroundColor: "rgba(54, 162, 235, 0.6)",
                    borderColor: "rgba(54, 162, 235, 1)",
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            stepSize: 1
                        }
                    }
                }
            }
        });
    }

    // Gráfico de Turnos Disponíveis vs Ocupados
    const chartTurnosCanvas = document.getElementById("chartTurnos");
    if (chartTurnosCanvas && window.chartTurnosData) {
        new Chart(chartTurnosCanvas, {
            type: "doughnut",
            data: {
                labels: ["Vagas Ocupadas", "Vagas Disponíveis"],
                datasets: [{
                    data: [
                        window.chartTurnosData.ocupadas,
                        window.chartTurnosData.disponiveis
                    ],
                    backgroundColor: [
                        "rgba(255, 99, 132, 0.6)",
                        "rgba(75, 192, 192, 0.6)"
                    ],
                    borderColor: [
                        "rgba(255, 99, 132, 1)",
                        "rgba(75, 192, 192, 1)"
                    ],
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: "bottom"
                    }
                }
            }
        });
    }
});
