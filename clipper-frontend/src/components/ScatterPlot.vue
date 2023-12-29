<template>
    <div class="chart-container">
        <div class="chart-wrapper">
            <Scatter ref="scatter" :data="scatterData" :options="options" @mousemove="onClick" />
        </div>
    </div>
</template>

<style scoped>
.chart-container {
    display: flex;
    height: 70vh;
    /* Adjust as needed */
}

.chart-wrapper {
    max-width: 100%;
    width: 100%;
}
</style>

<script>
import {
    Chart as ChartJS,
    LinearScale,
    PointElement,
    LineElement,
    Tooltip,
    Legend
} from 'chart.js'
import {
    Scatter,
    getElementAtEvent
} from 'vue-chartjs'

ChartJS.register(LinearScale, PointElement, LineElement, Tooltip, Legend)

export default {
    name: 'ScatterPlot',
    components: {
        Scatter
    },
    props: {
        element: {
            type: Object,
            default: null
        },
        scatterData: {
            type: Object,
            default: null
        }
    },
    data() {
        return {
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    tooltip: {
                        callbacks: {
                            footer: function () {}
                        }
                    }
                }
            }
        }
    },
    methods: {
        elementAtEvent(element) {
            if (!element.length) {
                return
            }

            // if element is the same as before, do nothing
            const { datasetIndex, index } = element[0]
            if (this.scatterData.datasets[datasetIndex].label !== 'Image embeddings') {
                return
            }

            const newElement = this.scatterData.datasets[datasetIndex].data[index]

            if (this.element && this.element === newElement) {
                return
            }

            this.updateElement(newElement)
        },
        updateElement(newElement) {
            this.$emit('update:element', newElement)
        },
        onClick(event) {
            const chart = this.$refs.scatter.chart

            if (!chart) return

            this.elementAtEvent(getElementAtEvent(chart, event))
        },
        footerCallback(tooltipItems) {
            let selElement = null;
            tooltipItems.forEach((tooltipItem) => {
                let possibleSelElement = this.scatterData.datasets[tooltipItem.datasetIndex].data[tooltipItem.dataIndex];
                if (possibleSelElement && possibleSelElement.text) {
                    selElement = possibleSelElement;
                }
            });
            // if element has text property return it otherwise return empty string
            return selElement && selElement.text ? selElement.text : '';
        }
    },
    beforeMount() {
        this.options.plugins.tooltip.callbacks.footer = this.footerCallback;
    }
}
</script>
