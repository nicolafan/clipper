<template>
    <div class="chart-container">
        <div class="chart-wrapper">
            <Scatter ref="scatter" :data="data" :options="options" @mousemove="onClick"/>
        </div>
    </div>
</template>

<style scoped>
.chart-container {
    display: flex;
    height: 80vh;
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
import axios from 'axios'

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
        }
    },
    data() {
        return {
            data: {
                labels: [],
                datasets: [
                    {
                        label: 'Scatter Dataset',
                        data: [],
                        backgroundColor: 'rgba(255, 99, 132, 0.2)',
                        borderColor: 'rgb(255, 99, 132)',
                        borderWidth: 1
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false
            }
        }
    },
    methods: {
        loadDataset() {
            axios.get('/').then(response => {
                this.data = response.data
            }).catch(error => {
                console.log(error)
            })
        },
        elementAtEvent(element) {
            if (!element.length) {
                return
            }

            // if element is the same as before, do nothing
            const { datasetIndex, index } = element[0]
            const newElement = this.data.datasets[datasetIndex].data[index]
            
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
        }
    },
    mounted() {
        this.loadDataset()
    }
}
</script>
