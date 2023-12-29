<template>
    <div class="container-fluid mt-5">
        <div class="row">
            <div class="col-6">
                <ScatterPlot v-if="!isLoading" :scatterData="scatterData" :element="element"
                    @update:element="handleUpdateElement">
                </ScatterPlot>
                <div v-else class="d-flex justify-content-center align-items-center" style="height: 70vh;">
                    <div class="spinner-border" style="width: 3rem; height: 3rem;" role="status">
                        <span class="visually-hidden">Loading...</span>
                    </div>
                </div>
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
        <div class="row mt-3 bottom-fixed">
            <div class="col-6">
                <nav aria-label="Page navigation example">
                    <ul class="pagination justify-content-center">
                        <li v-for="page in pagesToDisplay" :key="page" class="page-item" style="cursor: pointer;">
                            <a class="page-link" :class="{ active: currentPage === page, disabled: page === '...' }"
                                @click="changePage(page)">{{ page }}</a>
                        </li>
                    </ul>
                </nav>
            </div>
            <div class="col-2">
                <div class="d-flex justify-content-center">
                    <input type="number" class="form-control" v-model="manualPage" placeholder="Or enter page number">
                    <button class="btn btn-primary ms-2" @click="changePage(manualPage)">Go</button>
                </div>
            </div>
        </div>
    </div>
</template>

<style scoped>
.bottom-fixed {
    position: fixed;
    bottom: 0;
    width: 100%;
}
</style>

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
            query: '',
            currentPage: 1,
            manualPage: null,
            nPages: 1,
            isLoading: false
        }
    },
    computed: {
        pagesToDisplay() {
            // if page is 1, display 1, 2, 3, ..., end
            // if page is 2, display 1, 2, 3, ..., end
            // if page is 3, display 1, ..., 2, 3, 4, ..., end
            // if page is n, display 1, ..., n-1, n, n+1, ..., end
            let pages = []
            let first = 1
            let last = this.nPages
            let start = Math.max(1, this.currentPage - 1)
            let end = Math.min(this.currentPage + 1, last)
            pages.push(first)
            for (let i = start; i <= end; i++) {
                pages.push(i)
            }
            pages.push(last)

            // remove duplicates
            pages = pages.filter((page, index) => pages.indexOf(page) === index)

            // if element i is not equal to i+1, add '...'
            let newPages = []
            for (let i = 0; i < pages.length; i++) {
                newPages.push(pages[i])
                if (i === pages.length - 1) {
                    break
                }
                if (pages[i] !== pages[i + 1] - 1) {
                    newPages.push('...')
                }
            }

            return newPages
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
        changePage(page) {
            if (page === '...') {
                return
            }
            this.currentPage = page
            this.loadDataset(this.currentPage)
        },
        loadDataset(page) {
            this.isLoading = true
            axios.get('/' + page).then(response => {
                let newScatterData = JSON.parse(JSON.stringify(this.scatterData))
                let imageEmbeddingsDataset = newScatterData.datasets.find(dataset => dataset.label === 'Image embeddings')
                imageEmbeddingsDataset.data = response.data.dataset
                this.scatterData = newScatterData

                this.nPages = response.data.nPages
                this.isLoading = false
            }).catch(error => {
                console.log(error)
                this.isLoading = false
            })
        },
    },
    mounted() {
        this.loadDataset(this.currentPage)
    }
}
</script>