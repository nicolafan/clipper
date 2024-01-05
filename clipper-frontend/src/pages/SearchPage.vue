<template>
    <div class="container-fluid mt-5">
        <div class="row">
            <div class="col-3" />
            <div class="col-6">
                <div class="d-flex justify-content-between">
                    <div class="col-9 pe-2">
                        <input type="text" class="form-control" v-model="searchQuery" placeholder="Enter your query here">
                    </div>
                    <div class="col-3">
                        <button class="btn btn-primary" @click="search">Search</button>
                    </div>
                </div>
            </div>
        </div>
        <div v-if="searchResults" class="gallery mt-5">
            <template v-for="(result, index) in searchResults.ids[0]" :key="index">
                <div style="position: relative;">
                    <!-- show image only if the url works -->
                    <img :src="'data:image/jpeg;base64,' + searchResults.images[0][index]" alt="Image"
                        @mouseover="selectedImage = result; calculateCardPosition($event)"
                        @mouseleave="selectedImage = null" :class="{ 'hovered-image': selectedImage === result }">
                    <transition name="fade">
                        <div v-if="selectedImage === result" class="card image-card" :style="{ [cardPosition]: '0' }"
                            @mouseover="selectedImage = result;" @mouseleave="selectedImage = null">
                            <div class="card-header">{{ result }}</div>
                            <div class="card-body">
                                <div class="card-text">
                                    <b>Similarity: </b> {{ (1 - searchResults.distances[0][index]).toFixed(2) }}
                                    <template v-for="(value, key) in searchResults.metadatas[0][index]" :key="key">
                                        <div>
                                            <b>{{ key }}:</b> {{ value }}
                                        </div>
                                    </template>
                                </div>
                            </div>
                        </div>
                    </transition>
                    <transition name="fade">
                        <div v-if="selectedImage !== result" class="overlay">
                            {{ (1 - searchResults.distances[0][index]).toFixed(2) }}
                        </div>
                    </transition>
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
    width: 100%;
    height: auto;
    object-fit: cover;
    border-radius: 5px;
    /* center image */
    display: block;
    margin-left: auto;
    margin-right: auto;
}

.hovered-image {
    opacity: 0.8;
    /* add border of boostrap primary color */
    border: 6px solid #0d6efd;
}

.image-card {
    position: absolute;
    top: 30%;
    left: 100%;
    transform: translate(-50%, -50%);
    z-index: 1;
    width: max-content;
}

.overlay {
    position: absolute;
    bottom: 0;
    right: 0;
    background: rgba(0, 0, 0, 0.5);
    color: white;
    padding: 5px;
}

.fade-enter-active,
.fade-leave-active {
    transition: opacity .5s;
}

.fade-enter,
.fade-leave-to {
    opacity: 0;
}
</style>
<script>
import axios from 'axios'

export default {
    name: 'SearchPage',
    data() {
        return {
            searchQuery: '',
            searchResults: null,
            selectedImage: null,
            cardPosition: 'right'
        }
    },
    methods: {
        search() {
            axios.get('/search', {
                params: {
                    query: this.searchQuery
                }
            }).then((response) => {
                this.searchResults = response.data;
            })
        },
        getImage(id) {
            axios.get('/get_image/' + id)
                .then(response => {
                    this.image = response.data.image;
                })
                .catch(error => {
                    console.log(error);
                })
        },
        calculateCardPosition(event) {
            const imageRect = event.target.getBoundingClientRect();
            const spaceOnRight = window.innerWidth - imageRect.right;
            const spaceOnLeft = imageRect.left;
            if (spaceOnRight >= spaceOnLeft) {
                this.cardPosition = 'right';
            } else {
                this.cardPosition = 'left';
            }
        }
    }
}
</script>