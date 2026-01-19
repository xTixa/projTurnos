document.addEventListener("DOMContentLoaded", function () {
    // Common Chart Options
    Chart.defaults.font.family = "'Inter', system-ui, -apple-system, sans-serif";
    Chart.defaults.color = '#64748b';

    // Gráfico de Alunos por UC
    const chartAlunosCanvas = document.getElementById("chartAlunos");
    if (chartAlunosCanvas && window.chartAlunosData) {
        const ctxAlunos = chartAlunosCanvas.getContext('2d');
        const gradientAlunos = ctxAlunos.createLinearGradient(0, 0, 0, 400);
        gradientAlunos.addColorStop(0, '#60a5fa'); // Blue-400 (Softer)
        gradientAlunos.addColorStop(1, '#93c5fd'); // Blue-300 (Light)

        new Chart(chartAlunosCanvas, {
            type: "bar",
            data: {
                labels: window.chartAlunosData.labels,
                datasets: [{
                    label: "Alunos",
                    data: window.chartAlunosData.values,
                    backgroundColor: gradientAlunos,
                    borderRadius: 6,
                    barThickness: 30,
                    hoverBackgroundColor: '#3b82f6'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        backgroundColor: '#0f172a',
                        padding: 12,
                        titleColor: '#fff',
                        bodyColor: '#e2e8f0',
                        cornerRadius: 6,
                        displayColors: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        grid: {
                            color: '#f1f5f9',
                            drawBorder: false
                        },
                        ticks: {
                            color: '#64748b',
                            font: { size: 11 }
                        }
                    },
                    x: {
                        grid: { display: false },
                        ticks: {
                            color: '#64748b',
                            font: { size: 11 }
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
                labels: ["Ocupadas", "Disponíveis"],
                datasets: [{
                    data: [
                        window.chartTurnosData.ocupadas,
                        window.chartTurnosData.disponiveis
                    ],
                    backgroundColor: [
                        "#60a5fa", // Ocupadas (Blue-400 - Softer)
                        "#b6d6ff"  // Disponíveis (Slate-200 - Light Grey)
                    ],
                    borderWidth: 0,
                    hoverOffset: 4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                cutout: '75%',
                plugins: {
                    legend: {
                        position: "right",
                        labels: {
                            usePointStyle: true,
                            pointStyle: 'circle',
                            padding: 20,
                            font: { size: 12, family: "'Inter', sans-serif" },
                            color: '#475569'
                        }
                    }
                }
            }
        });
    }
});
