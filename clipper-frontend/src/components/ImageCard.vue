<template>
    <div class="card mt-4">
        <div v-if="element" class="card-header">
            {{ element.id }}
        </div>
        <div class="card-body">
            <div class="image-container">
                <img :src="'data:image/jpeg;base64,' + image" alt="Image" />
            </div>
            <div v-if="element" class="card-text">
                <div v-for="(value, key) in element.metadata" :key="key">
                    <b>{{ key }}:</b> {{ value }}
                </div>
            </div>
        </div>
    </div>
</template>

<style scoped>
.image-container {
    display: flex;
    justify-content: center;
    height: 40vh;
}

.image-container img {
    width: auto;
    height: auto;
    max-width: 80%;
    max-height: 80%;
    object-fit: contain;
    border-radius: 10px;
}
</style>
<script>
import axios from 'axios'

export default {
    name: 'ImageCard',
    components: {
    },
    props: {
        element: {
            type: Object,
            default: null
        }
    },
    data() {
        return {
            image: null
        }
    },
    watch: {
        element: 'getImage'
    },
    methods: {
        getImage() {
            if (!this.element) {
                return
            }
            axios.get('/get_image/' + this.element.id)
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