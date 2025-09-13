// Report Page JavaScript
class ReportCharts {
  constructor() {
    this.charts = {};
    this.colors = {
      // Soft pastel palette for better contrast and modern look
      primary: '#4E79A7',      // Soft blue
      success: '#59A14F',      // Soft green
      warning: '#F28E2B',      // Soft orange
      danger: '#E15759',       // Soft red
      info: '#76B7B2',         // Soft teal
      secondary: '#B07AA1',    // Soft purple
      lightBlue: '#A0CBE8',    // Light blue
      lightOrange: '#FFBE7D',  // Light orange
      lightGreen: '#8CD17D',   // Light green
      lightPurple: '#D4A6C8',  // Light purple
      lightTeal: '#A9D0D6',    // Light teal
      lightRed: '#F4A6A7'      // Light red
    };
    
    this.init();
  }

  init() {
    this.setupEventListeners();
    this.configureChartDefaults();
    this.createCharts();
  }

  configureChartDefaults() {
    // Set default font for all Chart.js instances
    if (typeof Chart !== 'undefined') {
      Chart.defaults.font.family = "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif";
      Chart.defaults.font.size = 12;
    }
  }

  setupEventListeners() {
    window.addEventListener('resize', () => {
      Object.values(this.charts).forEach(chart => {
        if (chart && typeof chart.resize === 'function') {
          chart.resize();
        }
      });
    });
  }

  // Utility Functions
  formatCurrency(value) {
    if (value >= 1000000) {
      return '$' + (value / 1000000).toFixed(1) + 'M';
    } else if (value >= 1000) {
      return '$' + (value / 1000).toFixed(0) + 'K';
    } else {
      return '$' + value.toFixed(0);
    }
  }

  formatPercent(value, total) {
    return Math.round((value / total) * 100);
  }

  shortenLabel(label, maxLength = 14) {
    if (label.length <= maxLength) return label;
    return label.substring(0, maxLength - 3) + '...';
  }

  // Chart Creation Methods
  createCharts() {
    this.createStatusChart();
    this.createBilledPaidChart();
    this.createUnderpaymentChart();
  }

  createStatusChart() {
    const ctx = document.getElementById('statusChart');
    if (!ctx) return;

    const data = window.statusData;
    if (!data || !data.labels || data.labels.length === 0) {
      this.showChartError('statusChart', 'No status data available');
      return;
    }

    const total = data.data.reduce((sum, value) => sum + value, 0);
    
    this.charts.status = new Chart(ctx, {
      type: 'doughnut',
      data: {
        labels: data.labels,
        datasets: [{
          data: data.data,
          backgroundColor: [
            this.colors.primary,    // Soft blue for Under Review
            this.colors.success,    // Soft green for Paid
            this.colors.danger      // Soft red for Denied
          ],
          borderWidth: 2,
          borderColor: '#ffffff',
          cutout: '60%'
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          title: {
            display: true,
            text: 'Claims by Status',
            font: {
              family: "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
              size: 16,
              weight: '600'
            },
            color: '#1f2937'
          },
          legend: {
            position: window.innerWidth >= 768 ? 'right' : 'bottom',
            labels: {
              usePointStyle: true,
              padding: 20,
              font: {
                family: "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
                size: 12
              },
              generateLabels: (chart) => {
                const data = chart.data;
                return data.labels.map((label, index) => {
                  const value = data.datasets[0].data[index];
                  const percentage = this.formatPercent(value, total);
                  return {
                    text: `${label} — ${percentage}%`,
                    fillStyle: data.datasets[0].backgroundColor[index],
                    strokeStyle: data.datasets[0].borderColor || data.datasets[0].backgroundColor[index],
                    lineWidth: 1,
                    pointStyle: 'circle'
                  };
                });
              }
            }
          },
          tooltip: {
            backgroundColor: '#ffffff',
            titleColor: '#1f2937',
            bodyColor: '#374151',
            borderColor: '#e5e7eb',
            borderWidth: 1,
            cornerRadius: 8,
            displayColors: true,
            callbacks: {
              label: (context) => {
                const label = context.label;
                const value = context.parsed;
                const percentage = this.formatPercent(value, total);
                return `${label} • ${value.toLocaleString()} claims (${percentage}%)`;
              }
            }
          }
        }
      }
    });
  }

  createBilledPaidChart() {
    const ctx = document.getElementById('billedPaidChart');
    if (!ctx) return;

    const data = window.billedPaidData;
    if (!data || data.length === 0) {
      this.showChartError('billedPaidChart', 'No billing data available');
      return;
    }

    const labels = data.map(item => this.shortenLabel(item.insurer, 12));
    const billedData = data.map(item => item.billed);
    const paidData = data.map(item => item.paid);

    this.charts.billedPaid = new Chart(ctx, {
      type: 'bar',
      data: {
        labels: labels,
        datasets: [
          {
            label: 'Billed',
            data: billedData,
            backgroundColor: this.colors.lightBlue,
            borderColor: this.colors.primary,
            borderWidth: 1,
            borderRadius: 6,
            maxBarThickness: 40,
            hoverBackgroundColor: this.colors.primary,
            hoverBorderWidth: 2
          },
          {
            label: 'Paid',
            data: paidData,
            backgroundColor: this.colors.lightGreen,
            borderColor: this.colors.success,
            borderWidth: 1,
            borderRadius: 6,
            maxBarThickness: 40,
            hoverBackgroundColor: this.colors.success,
            hoverBorderWidth: 2
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          title: {
            display: true,
            text: 'Billed vs Paid by Insurer',
            font: {
              family: "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
              size: 16,
              weight: '600'
            },
            color: '#1f2937'
          },
          legend: {
            position: 'top',
            labels: {
              usePointStyle: true,
              padding: 20,
              font: {
                size: 12
              }
            }
          },
          tooltip: {
            backgroundColor: '#ffffff',
            titleColor: '#1f2937',
            bodyColor: '#374151',
            borderColor: '#e5e7eb',
            borderWidth: 1,
            cornerRadius: 8,
            displayColors: true,
            callbacks: {
              title: (context) => {
                const index = context[0].dataIndex;
                return data[index].insurer;
              },
              label: (context) => {
                const value = context.parsed.y;
                return `${context.dataset.label}: ${this.formatCurrency(value)}`;
              }
            }
          }
        },
        scales: {
          x: {
            ticks: {
              maxRotation: 30,
              minRotation: 0,
              font: {
                family: "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
                size: 11
              },
              color: '#374151'
            },
            grid: {
              display: false
            }
          },
          y: {
            beginAtZero: true,
            ticks: {
              callback: (value) => this.formatCurrency(value),
              font: {
                size: 11
              }
            },
            grid: {
              color: '#e5e7eb',
              drawBorder: false
            }
          }
        }
      }
    });
  }

  createUnderpaymentChart() {
    const ctx = document.getElementById('underpaymentChart');
    if (!ctx) return;

    const data = window.underpaymentData;
    if (!data || data.length === 0) {
      this.showChartError('underpaymentChart', 'No underpayment data available');
      return;
    }

    // Sort by average underpayment descending
    const sortedData = [...data].sort((a, b) => b.avg_underpayment - a.avg_underpayment);
    const labels = sortedData.map(item => this.shortenLabel(item.insurer, 16));
    const values = sortedData.map(item => item.avg_underpayment);

    this.charts.underpayment = new Chart(ctx, {
      type: 'bar',
      data: {
        labels: labels,
        datasets: [{
          label: 'Average Underpayment',
          data: values,
          backgroundColor: values.map(value => 
            value > 200000 ? this.colors.lightRed :
            value > 100000 ? this.colors.lightOrange :
            this.colors.lightGreen
          ),
          borderColor: values.map(value => 
            value > 200000 ? this.colors.danger :
            value > 100000 ? this.colors.warning :
            this.colors.success
          ),
          borderWidth: 1,
          borderRadius: 6,
          maxBarThickness: 30,
          hoverBackgroundColor: values.map(value => 
            value > 200000 ? this.colors.danger :
            value > 100000 ? this.colors.warning :
            this.colors.success
          ),
          hoverBorderWidth: 2
        }]
      },
      options: {
        indexAxis: 'y',
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          title: {
            display: true,
            text: 'Average Underpayment by Insurer',
            font: {
              family: "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
              size: 16,
              weight: '600'
            },
            color: '#1f2937'
          },
          legend: {
            display: false
          },
          tooltip: {
            backgroundColor: '#ffffff',
            titleColor: '#1f2937',
            bodyColor: '#374151',
            borderColor: '#e5e7eb',
            borderWidth: 1,
            cornerRadius: 8,
            displayColors: true,
            callbacks: {
              title: (context) => {
                const index = context[0].dataIndex;
                return sortedData[index].insurer;
              },
              label: (context) => {
                const value = context.parsed.x;
                return `Average Underpayment: ${this.formatCurrency(value)}`;
              }
            }
          },
          datalabels: {
            display: true,
            anchor: 'end',
            align: 'right',
            color: '#374151',
            font: {
              family: "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
              size: 11,
              weight: '600'
            },
            formatter: (value) => this.formatCurrency(value)
          }
        },
        scales: {
          x: {
            beginAtZero: true,
            ticks: {
              callback: (value) => this.formatCurrency(value),
              font: {
                family: "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
                size: 11
              },
              color: '#374151'
            },
            grid: {
              color: '#e5e7eb',
              drawBorder: false
            }
          },
          y: {
            ticks: {
              font: {
                family: "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
                size: 11
              },
              color: '#374151'
            },
            grid: {
              display: false
            }
          }
        }
      },
      plugins: typeof ChartDataLabels !== 'undefined' ? [ChartDataLabels] : []
    });
  }

  showChartError(containerId, message) {
    const container = document.getElementById(containerId);
    if (container) {
      container.innerHTML = `<div class="chart-error">${message}</div>`;
    }
  }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
  // Load Chart.js and ChartDataLabels
  const loadChartJS = () => {
    if (typeof Chart === 'undefined') {
      const script = document.createElement('script');
      script.src = 'https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.js';
      script.onload = () => {
        loadDataLabels();
      };
      script.onerror = () => {
        console.error('Failed to load Chart.js');
        // Fallback: show error messages
        document.querySelectorAll('.chart-container').forEach(container => {
          container.innerHTML = '<div class="chart-error">Failed to load chart library</div>';
        });
      };
      document.head.appendChild(script);
    } else {
      loadDataLabels();
    }
  };

  const loadDataLabels = () => {
    if (typeof ChartDataLabels === 'undefined') {
      const script = document.createElement('script');
      script.src = 'https://cdn.jsdelivr.net/npm/chartjs-plugin-datalabels@2.2.0/dist/chartjs-plugin-datalabels.min.js';
      script.onload = () => {
        new ReportCharts();
      };
      script.onerror = () => {
        console.warn('Failed to load ChartDataLabels plugin, continuing without data labels');
        new ReportCharts();
      };
      document.head.appendChild(script);
    } else {
      new ReportCharts();
    }
  };

  loadChartJS();
});
