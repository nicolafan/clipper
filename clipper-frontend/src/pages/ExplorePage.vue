<template>
    <div class="container-fluid mt-5">
        <div class="row">
            <div class="col-6">
                <ScatterPlot :scatterData="scatterData" :element="element" @update:element="handleUpdateElement">
                </ScatterPlot>
            </div>
            <div class="col-6">
                <div class="d-flex justify-content-between">
                    <div class="col-9 pe-2">
                        <input type="text" class="form-control" v-model="query" placeholder="Enter your query here">
                    </div>
                    <div class="col-3">
                        <button class="btn btn-primary" @click="makeQuery">Make a query</button>
                    </div>
                </div>
                <ImageCard :element="element"></ImageCard>
            </div>
        </div>
    </div>
</template>

<style scoped></style>

<script>
import { reactive } from 'vue'
import ScatterPlot from '@/components/ScatterPlot.vue'
import ImageCard from '@/components/ImageCard.vue'

import axios from 'axios'

export default {
    name: 'ExplorePage',
    components: {
        ScatterPlot,
        ImageCard
    },
    data() {
        return {
            scatterData: reactive({
                labels: [],
                datasets: [
                    {
                        label: 'Queries',
                        data: [],
                        backgroundColor: '#0047ab',
                        borderColor: '#0047ab',
                        borderWidth: 1
                    }
                ]
            }),
            element: null,
            query: ''
        }
    },
    methods: {
        handleUpdateElement(element) {
            this.element = element
        },
        makeQuery() {
            if (!this.query) {
                return
            }

            axios.get('/query/' + this.query)
                .then(response => {
                    // make a copy of scatterData
                    let newScatterData = JSON.parse(JSON.stringify(this.scatterData))
                    // take dataset with label 'Queries'
                    let queriesDataset = newScatterData.datasets.find(dataset => dataset.label === 'Queries')
                    // if dataset with label 'New Query' exists add its data to the existing dataset
                    for (let i = 0; i < newScatterData.datasets.length; i++) {
                        if (newScatterData.datasets[i].label === 'New Query') {
                            queriesDataset.data.push(newScatterData.datasets[i].data[0])
                            // remove dataset with label 'New Query'
                            newScatterData.datasets.splice(i, 1)
                        }
                    }
                    // push new data to newScatterData.datasets
                    newScatterData.datasets.push(response.data)
                    // update scatterData
                    this.scatterData = newScatterData
                })
                .catch(error => {
                    console.log(error)
                })
        },
        loadDataset() {
            axios.get('/').then(response => {
                let newScatterData = JSON.parse(JSON.stringify(this.scatterData))
                newScatterData.datasets.push(response.data)
                this.scatterData = newScatterData
            }).catch(error => {
                console.log(error)
            })
        },
    },
    mounted() {
        this.loadDataset()
    }
}
</script>