<template>
    <div>
      <div class="Marker" v-for="date in markerDates" :style="{ left: calculatePosition(date) + 'vw' }" :key="date">
        </div>

        <div class="slider-component">
          <div class="slidecontainer">
            <input
              ref="input"
              v-model="currentValue"
              type="range"
              :min="min"
              :max="max"
              class="slider"
              @input="onInput"
            >
          </div>
        </div>

        


    </div>
  </template>
  
  <script>
  export default {
    props: {
      value: {
        type: Date,
        required: true
      },
      min: {
        type: Number,
        required: true
      },
      max: {
        type: Number,
        required: true
      },
      dates: {
        type: Array
      },
    },
    data(){
      return {
        currentValue: this.value.getTime(),
        markerDates: [],
      };
    },
    methods: {
      onInput() {
        // this.currentValue is a string because HTML is weird
        this.$emit('input', parseInt(this.currentValue));
      },
      calculatePosition(date){
        if (this.min <= date && date <= this.max)
          return (date - this.min) / (this.max - this.min) * 55 + 25;

        return -200;
        
      }
    },
    watch: {
      value(newValue) {
        this.currentValue = newValue.getTime();
      },
      dates: {
        handler: function(newDate){
          this.markerDates = newDate;
        },
        deep: true,
      }

    }
  };
  </script>
  
  <style scoped>
.Marker{
  height: 3vh;
  width: 0.2vw;

  background: rgb(90, 40, 40);
  position: absolute;
  top: 3vh;
  user-select: none;
        -moz-user-select: none;
        -khtml-user-select: none;
        -webkit-user-select: none;
        -o-user-select: none;
}

  .slider-component .slidecontainer {
      width: 55vw;
      height: 10vh;

      display: flex;
      justify-content: center;
      align-items: center;
  }
  
  .slider-component .slidecontainer .slider {
      -webkit-appearance: none;
      appearance: none;
      width: 100%;
      height: 4px;
      border-radius: 2px;
      background: #d8d8d8;
      outline: none;
      opacity: 0.7;
      -webkit-transition: .2s;
      transition: opacity .2s;
  }
  
  .slider-component .slidecontainer .slider:hover {
      opacity: 1;
  }
  
  .slider-component .slidecontainer .slider::-webkit-slider-thumb {
      -webkit-appearance: none;
      appearance: none;
      width: 18px;
      height: 18px;
      background: #881313;
      cursor: pointer;
      border-radius: 50%;
  }
  
  .slider-component .slidecontainer .slider::-moz-range-thumb {
      width: 18px;
      height: 18px;
      background: #881313;
      cursor: pointer;
      border-radius: 50%;
  }
  </style>
  