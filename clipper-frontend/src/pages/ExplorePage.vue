<template>
    <div class="container-fluid mt-5">
        <div class="row">
            <div class="col-6">
                <ScatterPlot :element="element" @update:element="handleUpdateElement"></ScatterPlot>
            </div>
            <div class="col-6">
                <ImageCard :element="element"></ImageCard>
            </div>
        </div>
    </div>
</template>

<style scoped>
</style>

<script>
import ScatterPlot from '@/components/ScatterPlot.vue'
import ImageCard from '@/components/ImageCard.vue'

export default {
    name: 'ExplorePage',
    components: {
        ScatterPlot,
        ImageCard
    },
    data() {
        return {
            element: null
        }
    },
    methods: {
        handleUpdateElement(element) {
            this.element = element
        }
    }
}
</script>