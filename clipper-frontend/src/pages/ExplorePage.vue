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
                        label: 'New text query',
                        fill: false,
                        borderColor: '#00ffff',
                        backgroundColor: '#00ffff',
                        data: [],
                        radius: 5,
                        hoverRadius: 8,
                    },
                    {
                        label: 'Text queries',
                        fill: false,
                        borderColor: '#0047ab',
                        backgroundColor: '#0047ab',
                        data: [],
                        radius: 3,
                        hoverRadius: 6
                    },
                    {
                        label: "Image embeddings",
                        fill: false,
                        borderColor: '#f87979',
                        backgroundColor: '#f87979',
                        data: [],
                        radius: 5,
                        hoverRadius: 8
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
                    let newScatterData = JSON.parse(JSON.stringify(this.scatterData))
                    let textQueriesDataset = newScatterData.datasets.find(dataset => dataset.label === 'Text queries')
                    let newTextQueryDataset = newScatterData.datasets.find(dataset => dataset.label === 'New text query')
                    
                    // append newTextQueryDataset to textQueriesDataset
                    textQueriesDataset.data.push(...newTextQueryDataset.data)
                    newTextQueryDataset.data = response.data

                    this.scatterData = newScatterData
                })
                .catch(error => {
                    console.log(error)
                })
        },
        loadDataset() {
            axios.get('/').then(response => {
                let newScatterData = JSON.parse(JSON.stringify(this.scatterData))
                let imageEmbeddingsDataset = newScatterData.datasets.find(dataset => dataset.label === 'Image embeddings')
                imageEmbeddingsDataset.data = response.data
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