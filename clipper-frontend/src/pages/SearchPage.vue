<template>
    <div class="container-fluid mt-5">
        <div class="row">
            <div class="col-4" />
            <div class="col-4">
                <div class="d-flex justify-content-between">
                    <div class="col-9 pe-2">
                        <input type="text" class="form-control" v-model="searchQuery" placeholder="Enter your query here">
                    </div>
                    <div class="col-3">
                        <button class="btn btn-primary" @click="search">Make a query</button>
                    </div>
                </div>
            </div>
            <div class="col-4" />
        </div>
        <div v-if="searchResults" class="gallery mt-5">
            <template v-for="(result, index) in searchResults.ids[0]" :key="index">
                <div>
                    <!-- show image only if the url works -->
                    <img :src="'data:image/jpeg;base64,' + searchResults.images[0][index]" alt="Image">
                </div>
            </template>
        </div>
    </div>
</template>

<style scoped>
.gallery {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    grid-gap: 20px;
    margin-top: 20px;
}

.gallery img {
    width: 90%;
    height: auto;
    object-fit: cover;
    border-radius: 5px;
    /* center image */
    display: block;
    margin-left: auto;
    margin-right: auto;
    cursor: pointer;
}
</style>
<script>
import axios from 'axios'

export default {
    name: 'SearchPage',
    data() {
        return {
            searchQuery: '',
            searchResults: null
        }
    },
    methods: {
        search() {
            axios.get('/search', {
                params: {
                    query: this.searchQuery
                }
            }).then((response) => {
                this.searchResults = response.data
            })
        },
        getImage(id) {
            axios.get('/get_image/' + id)
                .then(response => {
                    this.image = response.data.image
                })
                .catch(error => {
                    console.log(error)
                })
        }
    }
}
</script>