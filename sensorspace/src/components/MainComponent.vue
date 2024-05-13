<script>
import nodeGraph from "./nodeGraph.vue"
import '@vuepic/vue-datepicker/dist/main.css';

import sliderComponent from "./sliderComponent.vue";



export default {
  components: {nodeGraph, sliderComponent},
  data() {
    return {
      addedItems: 0,
      removedItems: 0,
      totalNodes: 0,
      totalMachines: 0,
      devices: {},
      date: [new Date(), new Date()],
      currentDate: new Date(),
      playing: true,
      selectedNode: null,
      selectedNodeInfo: {},
      selectedNodeName: "",
      showSettings: false,
      colorScheme: "Dark",
      showNotifications: false,
      notifications: {},
      prevDevices: {},
      deviceList: [],
      playbackSpeed: 1,
      dateTimestamps: [],
      notificationsUnread: false,
      dateTimestampsByIp: {},
      
    }
  },

  watch: {
    devices: {
      handler: function(newVal){
        if (newVal == null) return;
       
      },
      deep: true
    }
  },  

  mounted(){
    this.fetchNewData();
    
  },
  methods: {
    fetchNewData(){


      let results = []
   
      for (let i = 0; i < 135; i++){
        fetch(`/network-visualizer/day_files/${i}.json`).then(response => {

        return response.json();
      }).then(json => { 
    
        results.push(json);
        

        if (results.length == 135){
          let entries = this.get_entries(results);
      
          // Setup the date
          this.date = this.get_date(entries);
          this.currentDate = this.date[0];
        
          // Push out entries and assign lifepsans
          this.deviceList = this.get_devices(entries);
          [this.dateTimestamps, this.dateTimestampsByIp] = this.get_timestamps(this.deviceList);

          this.playThroughDate(true);
        }
      })
      }
      
 
      // fetch("http://localhost:2204/get_day_files").then(response => {
      //   return response.json();
      // }).then(json => {
      //   // Grab all entries and organize them by date and IP
      //   let entries = this.get_entries(json);
     
      //   // Setup the date
      //   this.date = this.get_date(entries);
      //   this.currentDate = this.date[0];
      
      //   // Push out entries and assign lifepsans
      //   this.deviceList = this.get_devices(entries);
      //   [this.dateTimestamps, this.dateTimestampsByIp] = this.get_timestamps(this.deviceList);
      // })
    },
    get_timestamps(devices){
      let timestamps = [];
      let timestampsWithIP = {};

      for (const deviceName in devices){
        let timestamp = devices[deviceName]["startDate"]
        timestamps.push(timestamp);

        if (!(timestamp in timestampsWithIP)){
          timestampsWithIP[timestamp] = [devices[deviceName]["ip"]];
        }else{
          timestampsWithIP[timestamp].push(devices[deviceName]["ip"]);
        }
        
      }


      return [timestamps, timestampsWithIP];
    },
    get_devices(entries){
      let deviceList = []
      let packages = {}
      let addedPackages, removedPackages;

      
      for (const entryName in entries){ 
        let [date, ip, entry] = entries[entryName];
  
        // Lifespan is the end date at which this device will be shown on the graph
        // Default it stays for 1 day, but is shortened if the device appears in a later file less then one day apart
        date = Date.parse(date);
        let endOfLifespan = date + 1000 * 60 * 60 * 24;

        // If this IP has existed in the past day shorten its lifespan to end before this snapshot
        for (const deviceIndex in deviceList){
          let device = deviceList[deviceIndex];
          if (device["ip"] == ip && device["endDate"] >= date){
            device["endDate"] = date - 1;
          }
        }

        // Checking for added packages
        [addedPackages, removedPackages, packages] = this.get_package_difference(packages, entry['All Packages Installed'], ip);
      
        // Add all these values as a new device in our final list
        deviceList.push({"startDate": date, "ip": ip, "entry": entry, "endDate": endOfLifespan, "Packages": packages[ip], "addedPackages": addedPackages, "removedPackages": removedPackages})
      }

      return deviceList;
    },
    get_package_difference(packages, devicePackages, ip){
      let removedPackages = {};
      let addedPackages = {};

      if (!(ip in packages)){ // If this is first time encountering the device then there is no previous packages to compare to 
        packages[ip] = Object.keys(devicePackages);
      }else{

        // Check for added / deleted packages using sets
        const set1 = new Set(packages[ip]);
        const set2 = new Set(Object.keys(devicePackages));
        
        // All packages in devicePackages but not in the last snapshot are added
        const newPackages = [...set2].filter(
            (element) => !set1.has(element));

        // Add every new package name/version to list and add it to the current package list
        for (const index in newPackages){
          let packageName = newPackages[index];


          
          addedPackages[packageName] = "1.0.0"
          
          packages[ip].push(packageName)
        }

        // All pacakges in the snapshot but not in the last snapshot are removed
        const deletedPackages = [...set1].filter(
            (element) => !set2.has(element));

        // Add every deleted package name/version to list and remove it from current package list
        for (const index in deletedPackages){
          let packageName = deletedPackages[index];
          if (packageName[0] == "x" || packageName[0] == "y" || packageName[0] == "z") continue;

          // let packageInfo = devicePackages[packageName];
          //removedPackages[packageName] = packageInfo["Installed Version"]
          removedPackages[packageName] = packageName
          packages[ip].splice(packages[ip].indexOf(packageName), 1)
        }

      }

      return [addedPackages, removedPackages, packages];
    },
    get_entries(json){
      // Gets every single entry given in the day files sorted by date
      let entries = [];
      for (const entry in json){
        let values = json[entry];
        let tracking = values["Tracking"];

        if (tracking == undefined)
          tracking = values[Object.keys(values)[0]];
        
        let ip = tracking["IP"];
        let date = tracking["Date"] + " " + tracking["Time"]

        entries.push([date, ip, json[entry]])

      }
      
      // Sort entries by date
      entries = entries.sort(function(a, b)  { 
        return Date.parse(a[0]) - Date.parse(b[0])
      });
    
      return entries
    },
    get_date(entries){
      let earliestDate = new Date(entries[0][0]);
      let latestDate = new Date(Date.parse(entries[entries.length - 1][0]) + 1000 * 60 * 60 * 24 * 7)

      // A couple example dates to explore test data
      // earliestDate = new Date("2/23/24 14:00");
      // latestDate = new Date(Date.parse(entries[entries.length - 1][0]) + 1000 * 60 * 60 * 1.5);

      // earliestDate = new Date("3/20/24 12:00");
      // latestDate = new Date(Date.parse(entries[entries.length - 1][0]) + 1000 * 60 * 60 * 8);

      //earliestDate = new Date("4/02/24 16:11:59");
      //latestDate = new Date(Date.parse(entries[entries.length - 1][0]) + 1000 * 60 * 1);

      earliestDate = new Date("4/04/24 15:03:00");
      latestDate = new Date("4/04/24 15:6:45")

      return [earliestDate, latestDate];
    },
    isDateInRange(dateToCheck, startDate, endDate) {
      // Remove time components from dates
      const dateToCheckWithoutTime = new Date(
          dateToCheck.getFullYear(),
          dateToCheck.getMonth(),
          dateToCheck.getDate()
      );
      const startDateWithoutTime = new Date(
          startDate.getFullYear(),
          startDate.getMonth(),
          startDate.getDate()
      );
      const endDateWithoutTime = new Date(
          endDate.getFullYear(),
          endDate.getMonth(),
          endDate.getDate()
      );

      // Check if the date falls within the range
      return (
          dateToCheckWithoutTime >= startDateWithoutTime &&
          dateToCheckWithoutTime <= endDateWithoutTime
      );
    },
    playThroughDate(dontStartPlaying){
      // If pressed manually either start or pause playing
      if (dontStartPlaying != true) this.playing = !this.playing;
      if (this.playing == false) return;

      this.currentDate = new Date(this.currentDate.getTime() + 60 * 60 * 24 * 1000 * 0.0033 * this.playbackSpeed * 0.001); // Adding 1 day to the current date
      this.$forceUpdate();
      
      if (this.currentDate > new Date("4/04/24 15:6:45")){
        this.currentDate = new Date("4/04/24 15:03:00");
      }

      // Setting up next iteration of playing
      if (this.playing){
        setTimeout(() => this.playThroughDate(true), 20);
      }else{
        this.playing = false;
      }

    },
    updateCurrentDate(newTime) {
      if (isNaN(newTime)) return;

      this.currentDate = new Date(newTime);
    },
    getFormattedCurrentDate(){
      // Returns current date in MM/DD/YY format
      return `${(this.currentDate.getMonth() + 1).toString().padStart(2, '0')}/${this.currentDate.getDate().toString().padStart(2, '0')}/${(this.currentDate.getFullYear() % 100).toString().padStart(2, '0')}`
    },
    addNotification(newNotification){
      console.log(newNotification);
      this.notifications[newNotification["key"]] = newNotification["value"];
      if (newNotification.dontUpdate != true) this.notificationsUnread = true;
    },
    changeSelectedNode(selectedNode){
      this.selectedNode = selectedNode["nodeName"];

      let node = selectedNode["node"];
      if (node == undefined) return;

      this.selectedNodeName = selectedNode["name"];
    

      if ("Device Descriptor" in node){ // Its a usb connected node
        let extraInfo = {};
     
        if ("Vendor and Product" in node){
         
          extraInfo = node["Vendor and Product"];
        }else{

          extraInfo = node["Device Descriptor"];
        } 

        this.selectedNodeInfo = extraInfo;

      }else{ // Its an ip node

    
        
        this.selectedNodeInfo = node["OS Device Information"];
      }
    }
   
  }

}
</script>

<template>
  <div :class="this.colorScheme" id="container">

    <div id="site-container">
      <div id="top-content">
        

      
        <h3 @click="playThroughDate" class="play-button">{{this.playing ? "||" : "▶"}}</h3>
    
        <h3 id="dateDisplay">{{(this.currentDate.getMonth() + 1).toString().padStart(2, '0')}}/{{this.currentDate.getDate().toString().padStart(2, '0')}}/{{(this.currentDate.getFullYear() % 100).toString().padStart(2, '0')}} {{this.currentDate.getHours().toString().padStart(2, '0')}}:{{this.currentDate.getMinutes().toString().padStart(2, '0')}}:{{this.currentDate.getSeconds().toString().padStart(2, '0')}}</h3>


        <h3 id="sliderContainer">
          <sliderComponent :dates="this.dateTimestamps" :value="this.currentDate" :min="this.date[0].getTime()" :max="this.date[1].getTime()" @input="updateCurrentDate"/>
        </h3>
        
        <h3 @click="this.showNotifications = true" :class="{notificationRed : this.notificationsUnread}" id="notification-button">{{this.notificationsUnread ? "❗" : "❕"}}</h3>
        <h3 @click="this.showSettings = true" id="settings-button">⚙</h3>
   
      </div>

      <div id="bottom-content">
        <div id="nodegraph">

          <nodeGraph :theme="colorScheme" @newNotification="addNotification" @selectedNodeChange="changeSelectedNode" :timestamps="dateTimestampsByIp" :date="currentDate" :devices="deviceList"/>
        </div>

        <div id="selectedNodeDisplay">
          <h2>{{ this.selectedNodeName }}</h2>

          <div id="extra-info-list">
            <h3 v-for="(value, key, index) in this.selectedNodeInfo" :key="index">
              {{ key }}: {{ value }}
            </h3>
          </div>
          
        </div>
      </div>
      
    </div>
    
    <div id="notifications" v-if="this.showNotifications">
      <div id="top-notifications-content">
        <h1>Notifications</h1>
        <h1 @click="this.showNotifications = false" id="exit-button">X</h1>
      </div>
      
      <div id="bottom-notifiations-content">
        <h3 v-for="(value, key, index) in this.notifications" :key="index">
              <span class="offsetColor">{{ key }}</span>: <h2 class="notification">{{ value }}</h2>
            </h3>
      </div>
    </div>

    <div id="settings" v-if="this.showSettings">
      <div id="top-settings-content">
        <h1>Settings</h1>
        <h1 @click="this.showSettings = false" id="exit-button">X</h1>
      </div>
      
      <div id="bottom-settings-content">
        <div id="color-select">
          <h2>Color Scheme: </h2>
          <h3 :class="this.colorScheme == 'Light' ? 'activeSetting' : ''" @click="this.colorScheme = 'Light'">Light Mode</h3>
          <h3 :class="{activeSetting: this.colorScheme=='Dark'}"  @click="this.colorScheme = 'Dark'">Dark Mode</h3>
        </div>
        <div id="playback-speed">
          <h2>Playback Speed: </h2>
          <input v-model="playbackSpeed">
        </div>
      </div>
    </div>

  </div>
  

</template>

<style scoped>


@import url('https://fonts.googleapis.com/css2?family=Inter&display=swap');

.Dark{
  --background-color: #101116;
  --background-offset-color: rgba(255, 255, 255, 0.01);
  --button-color: #1b1e22;
  --nodegraph-color: #14161a;
  --selection-panel-color: #181B1F;
  --secondary-text-color: rgb(204, 204, 204);
  --primary-text-color: rgb(229, 225, 225);
  --settings-background-color: #1b1e22;
  --nodegraph-inset-size: 5vw;
}

.Light{
 --background-color: #898989;
 --background-offset-color: rgba(0, 0, 0, 0.05);
 --button-color: #9096a0;
 --nodegraph-color: #d6d7da;
 --selection-panel-color: #8c949e;
 --secondary-text-color: rgb(29, 29, 29);
 --primary-text-color: rgb(0, 0, 0);
 --settings-background-color: #787e85;
 --nodegraph-inset-size: 2vw;
}

#playback-speed{
  display: flex;
  justify-content: space-evenly;
  width: 30vw;
  align-items: center;
  
}

.notificationRed{
  font-size: 3vw !important;
}

.offsetColor{
  color: rgb(172, 172, 172) !important;
}

.activeSetting{
  color: rgb(168, 168, 168);
  background: rgba(102, 102, 102, 0.438);
}

#bottom-settings-content{
  padding: 1vw;
  height: 30vh;

  display: flex;
  justify-content: space-evenly;
  align-items: left;
  flex-direction: column;

}

.notification{
  color: rgb(162, 24, 24);
}

#color-select{
  display: flex;
  justify-content: space-evenly;
  width: 30vw;
  align-items: center;
}

#exit-button{
  height: 5vh;
  width: 5vh;

  background: rgba(197, 70, 70, 0.329);
  border: solid rgba(83, 38, 38, 0.589) 1px;
  border-radius: 5px;

  display: flex;
  justify-content: center;
  align-items: center;
  font-size: 1vw;

  color: var(--secondary-text-color);
  box-shadow: inset 0 0 1vw rgb(0, 0, 0);
}

#top-notifications-content{
  background: rgb(0, 0, 0, 0.2);
  border-bottom: 3px solid rgb(34, 32, 32);
  width: 100%;
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 10vh;

  padding-left: 2vw;
  padding-right: 2vw;
}

#notifications{
  color: var(--secondary-text-color);
  background: var(--settings-background-color);
  border: solid rgb(77, 75, 75) 1px;
  border-radius: 25px;
  
  position: absolute;
  width: 40vw;
  height: 90vh;

  top: 5vh;
  left: 30vw;
  box-shadow: inset 0 0 var(--nodegraph-inset-size) rgb(0, 0, 0);
}

#top-settings-content{
  background: rgb(0, 0, 0, 0.2);
  border-bottom: 3px solid rgb(34, 32, 32);
  width: 100%;
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 10vh;

  padding-left: 2vw;
  padding-right: 2vw;
}

#settings{
  color: var(--secondary-text-color);
  background: var(--settings-background-color);
  border: solid rgb(12, 12, 12) 1px;
  border-radius: 25px;
  
  position: absolute;
  width: 70vw;
  height: 70vh;

  top: 15vh;
  left: 15vw;
}

#extra-info-list h3{
  word-wrap: break-word;
  text-align: center;
  padding-top: 4vh;
  width: 12vw;
  font-size: 0.8vw;
}


#bottom-notifiations-content h3{
  word-wrap: break-word;
  text-align: left;
  padding-left: 2vw;
  padding-bottom: 2vh;
  padding-top: 2vh;
  width: 100%;
  border-bottom: solid black 2px;
}

#selectedNodeDisplay h2{
  font-size: 1.25vw !important;
  width: 14vw;

  display: flex;
  justify-content: center;
  align-items: center;
}

#extra-info-list{
  width: 14vw;
  height: 60vh;

  font-size: 1vw;
  overflow-y: auto;
  scrollbar-width: thin;
  scrollbar-color: rgb(41, 41, 41) var(--selection-panel-color);

  display: flex;
  flex-direction: column;
  justify-content: space-evenly;
  align-items: center;
}

#nodegraph{
  width: 70vw;
  height: 80vh;

  background: var(--nodegraph-color);
  border: solid black 2px;
  border-radius: 15px;

  color: var(--primary-text-color);
  font-size: 1vw;

  border-radius: 15px 0 0 15px;
  box-shadow: inset 0 0 var(--nodegraph-inset-size) rgb(0, 0, 0);
}

#selectedNodeDisplay{
  width: 15vw;
  height: 80vh;
  border-radius: 15px;
  background: var(--selection-panel-color);
  border: solid black 2px;
  border-radius: 0 15px 15px 0;

  display: flex;
  flex-direction: column;
  justify-content: space-evenly;
  align-items: center;

  color:  var(--primary-text-color);
  font-size: 1vw;
  box-shadow: inset 0 0 1vw rgba(0, 0, 0, 0.352);
}

#bottom-content{
  flex-direction: row;
  display: flex !important;

  justify-content: space-evenly;
  align-items: center;

  width: 88vw;
  height: 83vh;


}


#dateDisplay{
  background: var(--button-color);
  width: 10vw;
  height: 10vh;

  border: solid black 1px;

  display: flex;
  justify-content: center;
  align-items: center;

  font-size: 1vw;
  color: var(--secondary-text-color);
  box-shadow: inset 0 0 0.25vw rgb(0, 0, 0);
}

#sliderContainer{
  background: var(--button-color);
  width: 60vw;
  height: 10vh;
  border: solid black 1px;

  display: flex;
  justify-content: center;
  align-items: center;

  border-radius: 0 0 0 0;
  box-shadow: inset 0 0 0.25vw rgb(0, 0, 0);
}

.play-button:hover,
#settings-button:hover,
#notification-button:hover{
  background: #141516;
  color: rgb(170, 169, 169);
}

.play-button:active,
#settings-button:hover,
#notification-button:hover{
  background: rgb(28, 29, 31);
}

#notification-button{
  box-shadow: inset 0 0 0.25vw rgb(0, 0, 0);
  width: 10vh;
  height: 10vh;
  background: var(--button-color);
  border-radius: 0 0 0 0;
  border: solid black 1px;
  display: flex;
  justify-content: center;
  align-items: center;

  font-size: 1.5vw;
  color: var(--secondary-text-color);
  -webkit-touch-callout: none; /* iOS Safari */
    -webkit-user-select: none; /* Safari */
     -khtml-user-select: none; /* Konqueror HTML */
       -moz-user-select: none; /* Old versions of Firefox */
        -ms-user-select: none; /* Internet Explorer/Edge */
            user-select: none; /* Non-prefixed version, currently
                                  supported by Chrome, Edge, Opera and Firefox */


}
#settings-button{
  box-shadow: inset 0 0 0.25vw rgb(0, 0, 0);
  width: 10vh;
  height: 10vh;
  background: var(--button-color);
  border-radius: 0 15px 15px 0;
  border: solid black 1px;
  display: flex;
  justify-content: center;
  align-items: center;

  font-size: 1.5vw;
  color: var(--secondary-text-color);
  -webkit-touch-callout: none; /* iOS Safari */
    -webkit-user-select: none; /* Safari */
     -khtml-user-select: none; /* Konqueror HTML */
       -moz-user-select: none; /* Old versions of Firefox */
        -ms-user-select: none; /* Internet Explorer/Edge */
            user-select: none; /* Non-prefixed version, currently
                                  supported by Chrome, Edge, Opera and Firefox */

  
}
.play-button{
  box-shadow: inset 0 0 0.25vw rgb(0, 0, 0);
  width: 10vh;
  height: 10vh;
  background: var(--button-color);
  border-radius: 15px 0 0 15px;
  border: solid black 1px;

  display: flex;
  justify-content: center;
  align-items: center;

  font-size: 1.5vw;
  color: var(--secondary-text-color);
  -webkit-touch-callout: none; /* iOS Safari */
    -webkit-user-select: none; /* Safari */
     -khtml-user-select: none; /* Konqueror HTML */
       -moz-user-select: none; /* Old versions of Firefox */
        -ms-user-select: none; /* Internet Explorer/Edge */
            user-select: none; /* Non-prefixed version, currently
                                  supported by Chrome, Edge, Opera and Firefox */
}

#dateSelector{
  width: 20vw;
}



body{
  margin: 0;
  padding: 0;
  font-family: 'Inter', sans-serif;
}



#top-content{
  display: flex;
  justify-content: space-evenly;
  align-items: center;
  width: 88vw;
  height: 8vh;

  color: white;
}

#site-container{
  background-color: var(--background-color); /* Slightly darker tan color */
  background-image: linear-gradient(
    45deg,
    var(--background-offset-color) 25%, /* Adjust the alpha value for smoother transition */
    transparent 25%,
    transparent 50%,
    var(--background-offset-color) 50%, /* Adjust the alpha value for smoother transition */
    var(--background-offset-color) 75%, /* Adjust the alpha value for smoother transition */
    transparent 75%,
    transparent
  );
  background-size: 40px 40px; /* Adjust the size of the simulated texture */
  height: 100vh; /* Adjust the height as needed */
  margin: 0;

  display: flex;
  justify-content: space-evenly;
  align-items: center;
  flex-direction: column;

  height: 100vh;
  width: 100vw;
}
  
.stat-display{
  background: #181B1F;
  color: white;
  width: 30vw;
  height: 25vh;

  border-radius: 15px;
  bordeR: solid black 2px;

  display: flex;
  justify-content: center;
  flex-direction: column;
  align-items: center;
}

</style>