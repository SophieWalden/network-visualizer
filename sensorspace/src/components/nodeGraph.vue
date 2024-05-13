<script>
import { rgb } from "d3";
import {
  ForceLayout,
} from "v-network-graph/lib/force-layout"

export default {
  components: {},
  props: ["devices", "date", "timestamps", "theme"],
  data() {
    return {
      prevTheme: "",
      lastDateMade: "",
      networkNames: [],
      packagesNames: [],
      nodes: {},
      edges: {},
      machineIPNodes: [],
      selectedNodes: [],
      dateOffset: 1,
      deviceCount: 0,
      radius: 100,
      dayLength: 60 * 60 * 24 * 1000,
      maliciousBosonNotifacationSent: 0,
      maliciousPackageNotificationSent: 0,
      lastDate: undefined,
      maliciousNodeActive: false,
      layouts: {nodes: {}},
      configs: {
        view: {
          layoutHandler: new ForceLayout({
            positionFixedByDrag: false,
            positionFixedByClickWithAltKey: true,
            createSimulation: (d3, nodes, edges) => {
                  const forceLink = d3.forceLink(edges).id(d => d.id);
                  const initialLinkDistance = 120; 
                  
              
                  const getLinkDistance = d => {
                      if (this.networkNames.includes(d.source.id)) {
                          return initialLinkDistance * 1.5; // Double the distance if the node is a network node
                      } else if(this.packagesNames.includes(d.source.id)){
                        return initialLinkDistance / 2; // Half distance if it is a package
                      } else {
                          return initialLinkDistance; 
                      }
                  };

                  forceLink.distance(d => getLinkDistance(d)).strength(1);

                 
                  const simulation = d3
                      .forceSimulation(nodes)
                      .force("edge", forceLink)
               
                      .force("center", d3.forceCenter().strength(0.01))
                    
                      .force("collision", d3.forceCollide().radius(d => this.machineIPNodes.includes(d.id) ? 25 : d.id == "Malicious Package192.168.1.26" ? 75 : 25
                      ))
                      .force("charge", d3.forceManyBody().strength(-1600))
                      .alphaMin(0.001);
                      

                  return simulation;
                      
              }
          }),
        },
      node: {
        selectable: true,
        normal: {
          type: "circle",
          radius: node => node.size,

          color: node => node.color
        },
        hover: {
          type: "circle",
          radius: node => node.size,
          // Other properties...
          color: "#5577dd", // Change the color here
        },
        selected: {
          type: "circle",
          radius: node => node.size,
          // Other properties...
          color: "#4466cc", // Change the color here
        },
        label: {
          visible: true,
          fontFamily: undefined,
          fontSize: node => node.label != undefined ? 24 : 11,
          lineHeight: node => node.label != undefined ? 5 : 1,
          color: node => node.theme == "Light" ? "black" : "white" ,
          margin: 4,
          direction: "south",
          background: {
            visible: false,
            color: "#FFFFFF" ,
            padding: {
              vertical: 1,
              horizontal: 4,
            },
            borderRadius: 2,
          },
        },
        focusring: {
          visible: true,
          width: 4,
          padding: 3,
          color: "#eebb00",
          dasharray: "0",
        },
      },
      edge: {
        selectable: true,
        normal: {
          width: 3,
          color: node => node.color,
          dasharray: "0",
          linecap: "butt",
          animate: true,
          animationSpeed: 50,
        },

      }
    }
    }
  },
  watch: { 
    devices: { handler: function() {

        this.updateDevices();
      }
    ,
    deep: true},
    date: { handler: function() {

        this.updateDevices();
        }
        ,
        deep: true},

    selectedNodes: {
      handler: function(newVal){
        let selectedNode = newVal[0];

        if (selectedNode in this.nodes){
        
          this.$emit("selectedNodeChange", {nodeName: selectedNode, node: this.nodes[selectedNode].nodeData, name: this.nodes[selectedNode].name});
        }

      }
    }
  },
  methods: {
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
    isNodeGreenMachines(devices, date, entry, ip){

      for (let i = 1; i <= this.dateOffset; i++){
        let previousDate = new Date(this.date - this.dayLength * i);
        let dateConversion = ((previousDate.getMonth() > 8) ? (previousDate.getMonth() + 1) : ('0' + (previousDate.getMonth() + 1))) + '/' + ((previousDate.getDate() > 9) ? previousDate.getDate() : ('0' + previousDate.getDate())) + '/' + (previousDate.getFullYear() % 100);

        if (Object.keys(this.devices).includes(dateConversion)){
          if (Object.keys(this.devices[dateConversion]).includes(ip)){
            return false;
          }
          
        }
      }

      return true;
    },
    isNodeGreenDevice(devices, date, entry, ip, device){

    for (let i = 1; i <= this.dateOffset; i++){
      let previousDate = new Date(this.date - this.dayLength * i);
      let dateConversion = ((previousDate.getMonth() > 8) ? (previousDate.getMonth() + 1) : ('0' + (previousDate.getMonth() + 1))) + '/' + ((previousDate.getDate() > 9) ? previousDate.getDate() : ('0' + previousDate.getDate())) + '/' + (previousDate.getFullYear() % 100);

      if (Object.keys(this.devices).includes(dateConversion)){
        if (Object.keys(this.devices[dateConversion]).includes(ip)){
          
          let devices = this.devices[entry][ip]["USB Devices"];
          
          if (Object.keys(devices).includes(device)){
            return false;
          }
        }
        
      }
    }

    return true;
    },
    formatDate(date) {
      // Get month, day, year, hours, and minutes
      var mm = date.getMonth() + 1; // Months are zero based
      var dd = date.getDate();
      var yy = date.getFullYear() % 100; // Get last two digits of the year
      var hh = date.getHours();
      var min = date.getMinutes();
      var sec = date.getSeconds();

      // Zero pad single digit days, months, hours, and minutes
      mm = (mm < 10 ? '0' : '') + mm;
      dd = (dd < 10 ? '0' : '') + dd;
      yy = (yy < 10 ? '0' : '') + yy;
      hh = (hh < 10 ? '0' : '') + hh;
      min = (min < 10 ? '0' : '') + min;
      sec = (sec < 10 ? '0' : '') + sec;

      // Return formatted date string
      return mm + '/' + dd + '/' + yy + ' ' + hh + ':' + min + ":" + sec;
  },
  renderMachineNode(device, ip){
    // Adds the main node for a certain ip to our nodes
    let nodeName = ip;
    let machineNodeImage = "https://upload.wikimedia.org/wikipedia/commons/thumb/0/02/Circle-icons-computer.svg/2048px-Circle-icons-computer.svg.png";
    let anchorNode = null;
    let size = 30;
    if (ip.includes("172.20.88.17")){
      machineNodeImage = "https://static.vecteezy.com/system/resources/previews/037/092/781/non_2x/robotic-arm-line-filled-circle-icon-vector.jpg";
      this.nodes[ip] = {name: "Operational Technology", isMachineIPNode: true, size: 24, theme: this.theme, nodeData: device["entry"], image: machineNodeImage}
      this.edges[ip + Math.random()] = {source: ip, target: "192.168.1.140", color:  "#062236", ip: ip}

      
      ip = "172.20.88.18"
      nodeName = "Operational Technology"
      anchorNode = "192.168.1.134";
      size = 24;

      let tempUrl = "https://cdn2.iconfinder.com/data/icons/technology-flat-line/70/microcontroller-512.png";
      this.nodes["1"] = {name: "Technology Controller", size: 16, theme: this.theme, nodeData: device, image: tempUrl , ip: ip};
      this.edges["2"] = {source: "1", target: "172.20.88.17", nodeData: {}, color:  "#062236", ip: ip}
      this.nodes["3"] = {name: "Technology Controller", size: 16, theme: this.theme, nodeData: device, image: tempUrl , ip: ip};
      this.edges["4"] = {source: "3", target: "172.20.88.18", nodeData: {}, color:  "#062236", ip: ip}

      this.nodes["7"] = {name: "USB Hub", size: 24, theme: this.theme, nodeData: device, image: tempUrl , ip: ip};
      this.edges["8"] = {source: "7", target: "172.20.88.16", nodeData: {}, color:  "#062236", ip: ip}

      this.nodes["24"] = {name: "USB Hub", size: 24, theme: this.theme, nodeData: device, image: tempUrl , ip: ip};
      this.edges["25"] = {source: "24", target: "172.20.88.16", nodeData: {}, color:  "#062236", ip: ip}
    }
    
    if (ip == "172.20.88.16"){
      machineNodeImage = "https://cdn-icons-png.freepik.com/512/3617/3617061.png"; // Machine is 3d printer
      nodeName = "Central Server"
      size = 48;
      
    } 
    if (ip.includes("192.168.1")){
      machineNodeImage = "https://projects.raspberrypi.org/images/hardware-cards/sensehat.svg";
      nodeName = "Rasberry Pi";
      anchorNode = "7";

      this.nodes[ip + "9"] = {name: nodeName, isMachineIPNode: true, size: size, theme: this.theme, nodeData: device["entry"], image: machineNodeImage}
      this.edges[ip + "9" + Math.random()] = {source: ip + "9", target: anchorNode, color:  "#062236", ip: ip}


      let networkImage = "https://cdn.icon-icons.com/icons2/614/PNG/512/wifi-symbol-inside-a-circle_icon-icons.com_56445.png";
      this.nodes[ip + "12"] = {name: "Ethernet Connection", size: 16, theme: this.theme, nodeData: device, image: networkImage , ip: ip};
      this.edges[ip + "9" + Math.random()] = {source: ip + "9", target: ip + "12", color:  "#062236", ip: ip}


      let tempUrl = "https://cdn2.iconfinder.com/data/icons/technology-flat-line/70/microcontroller-512.png";

      this.nodes[ip + "3"] = {name: "Operational Technology", isMachineIPNode: true, size: 24, theme: this.theme, nodeData: device["entry"], image: "https://static.vecteezy.com/system/resources/previews/037/092/781/non_2x/robotic-arm-line-filled-circle-icon-vector.jpg"}
      this.edges[ip + Math.random()] = {source: ip + "3", target: ip + "9", color:  "#062236", ip: ip}
      this.nodes[ip + "1"] = {name: "Technology Controller", size: 16, theme: this.theme, nodeData: device, image: tempUrl , ip: ip};
      this.edges[ip + "2"] = {source: ip + "1", target: ip + "3", nodeData: {}, color:  "#062236", ip: ip}
    

      let img = "https://static.vecteezy.com/system/resources/previews/037/143/357/non_2x/motion-sensor-flat-circle-icon-vector.jpg";
      this.nodes[ip + "10"] = {name: "Distance Sensor", isMachineIPNode: true, size: 16, theme: this.theme, nodeData: device["entry"], image: img}
      this.edges[ip + "10" + Math.random()] = {source: ip + "9", target: ip + "10", color:  "#062236", ip: ip}



      // Hub 2
      anchorNode = "24";

      this.nodes[ip + "9111"] = {name: nodeName, isMachineIPNode: true, size: size, theme: this.theme, nodeData: device["entry"], image: machineNodeImage}
      this.edges[ip + "9111" + Math.random()] = {source: ip + "9111", target: anchorNode, color:  "#062236", ip: ip}


      networkImage = "https://cdn.icon-icons.com/icons2/614/PNG/512/wifi-symbol-inside-a-circle_icon-icons.com_56445.png";
      this.nodes[ip + "12111"] = {name: "Ethernet Connection", size: 16, theme: this.theme, nodeData: device, image: networkImage , ip: ip};
      this.edges[ip + "9111" + Math.random()] = {source: ip + "9111", target: ip + "12111", color:  "#062236", ip: ip}


      tempUrl = "https://cdn2.iconfinder.com/data/icons/technology-flat-line/70/microcontroller-512.png";

      this.nodes[ip + "3111"] = {name: "Operational Technology", isMachineIPNode: true, size: 24, theme: this.theme, nodeData: device["entry"], image: "https://static.vecteezy.com/system/resources/previews/037/092/781/non_2x/robotic-arm-line-filled-circle-icon-vector.jpg"}
      this.edges[ip + Math.random()] = {source: ip + "3111", target: ip + "9111", color:  "#062236", ip: ip}
      this.nodes[ip + "1111"] = {name: "Technology Controller", size: 16, theme: this.theme, nodeData: device, image: tempUrl , ip: ip};
      this.edges[ip + "2111"] = {source: ip + "1111", target: ip + "3111", nodeData: {}, color:  "#062236", ip: ip}
    

      img = "https://static.vecteezy.com/system/resources/previews/037/143/357/non_2x/motion-sensor-flat-circle-icon-vector.jpg";
      this.nodes[ip + "10111"] = {name: "Distance Sensor", isMachineIPNode: true, size: 16, theme: this.theme, nodeData: device["entry"], image: img}
      this.edges[ip + "10111" + Math.random()] = {source: ip + "9111", target: ip + "10111", color:  "#062236", ip: ip}

      anchorNode = "7"
      
    }
    if (ip.includes("26")){
      nodeName = "Drone"
      machineNodeImage = "https://images.assetsdelivery.com/compings_v2/ahasoft2000/ahasoft20001604/ahasoft2000160400204.jpg";
      anchorNode = "Drone Anchor Node";

      

      let tempUrl = "https://cdn2.iconfinder.com/data/icons/technology-flat-line/70/microcontroller-512.png";
      this.nodes["Drone Anchor Node"] = {name: "USB Hub", size: 16, theme: this.theme, nodeData: device, image: tempUrl , ip: ip};
      this.edges["Drone Anchor Node Connection"] = {source: "Drone Anchor Node", target: "172.20.88.16", nodeData: {}, color:  "#062236", ip: ip}

      for (let i = 0; i < 3; i++){
        this.nodes[ip + "11" + i] = {name: "Drone", isMachineIPNode: true, size: 24, theme: this.theme, nodeData: device["entry"], image: machineNodeImage}
        this.edges[ip + "11" + Math.random()] = {source: ip + "11" + i, target: anchorNode, color:  "#062236", ip: ip}

        this.nodes[ip + "12" + i] = {name: "Drone Controller", isMachineIPNode: true, size: 16, theme: this.theme, nodeData: device["entry"], image: "https://media.istockphoto.com/id/1223128768/vector/white-wireless-gamepad-icon-isolated-with-long-shadow-game-controller-red-circle-button.jpg?s=612x612&w=0&k=20&c=F1NWU4lRoLD4W1NqLUqcE1cdB5wwBuIWgeyI7Xt5w0U="}
        this.edges[ip + "12" + Math.random()] = {source: ip + "12" + i, target: ip + "11" + i, color:  "#062236", ip: ip}
      }
    }


    // device["entry"]["Vendor and Product"]["Product"] = nodeName;
    this.nodes[ip] = {name: nodeName, isMachineIPNode: true, size: size, theme: this.theme, nodeData: device["entry"], image: machineNodeImage}

    if (anchorNode != null){

      this.edges[ip + Math.random()] = {source: ip, target: anchorNode, color:  "#062236", ip: ip}
    }

    this.machineIPNodes.push(ip);

    // Positioning the Node
    if (!(ip in this.layouts["nodes"])){
        let angle = (this.deviceCount / 5) * 2 * Math.PI;
        let x = this.radius * Math.cos(angle);
        let y = this.radius * Math.sin(angle);

        this.layouts["nodes"][ip] = {x: x, y: y}
        this.deviceCount += 1;
      }

    

  },
  renderUSBs(USBs, ip, startDate){
    if (ip.includes("172.20.88.17")) return;
    let seenDevicesNames = {}
    let maliciousRenders = 0; // For the demo
    let rendered = 0;
    for (const deviceIndex in USBs){
        let device = USBs[deviceIndex];

        let size = 16;
        let deviceName;
        if ("Vendor and Product" in device){
          deviceName = device["Vendor and Product"]["Product"];
        }else{
          deviceName = device["Device Descriptor"]["Device Class"];
        }
        
        let url = "https://winaero.com/blog/wp-content/uploads/2017/12/usb-flash-drive-icon-256-big.png";
        if (deviceName.includes("Controller")){
          url = "https://cdn2.iconfinder.com/data/icons/technology-flat-line/70/microcontroller-512.png";
          deviceName = "Controller";
          continue;
        }else if (deviceName.includes("hub")){
          if (!ip.includes("192.168.1.1")) continue;
          deviceName = ["Profilometer", "Proximity", "Air Flow", "Optical"][rendered];
          url = "https://cdn-icons-png.freepik.com/256/15038/15038808.png";
          rendered++;

        }else if (deviceName.includes("bad")){
          url = "https://images.assetsdelivery.com/compings_v2/stalkerstudent/stalkerstudent1602/stalkerstudent160201066.jpg";
        }else if(deviceName.includes("Boson")){
          url = "https://cdn-icons-png.freepik.com/512/3617/3617267.png";
          continue;
          deviceName = "Boson Camera";

          if (ip == "192.168.1.134" && maliciousRenders == 0){
            maliciousRenders = 1;
            deviceName = "Malicious Boson Camera";
            url = "https://icons.iconarchive.com/icons/martz90/circle/512/camera-icon.png";

            if (this.maliciousBosonNotifacationSent == 0){
              this.maliciousBosonNotifacationSent = 1;
              this.$emit("newNotification", {key: this.formatDate(new Date(startDate)), value: "Malicious Boson Detected @ IP " + ip, dontUpdate: true});
            }
            
          }
        }else if (deviceName.toLowerCase().includes("keyboard")){
          url = "https://cdn1.iconfinder.com/data/icons/education-flat-icons-circle-shadow-vol-2/96/64-512.png";
          deviceName = "Keyboard";
        }else if (deviceName.includes("USB2742") || deviceName.includes("USB5742")){
          url = "https://cdn-icons-png.freepik.com/512/7779/7779514.png";
          deviceName = "Hub Controller Chip";
        }else if (deviceName == "AX88179"){
          deviceName = "Ethernet Adapater";
          url = 'https://cdn-icons-png.freepik.com/256/573/573274.png';
        }else if (deviceName.includes("V3.0")){
          deviceName = "Database";
          url = "data:image/png;base64,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"
          size = 24;

          
          let networkImage = "https://cdn.icon-icons.com/icons2/614/PNG/512/wifi-symbol-inside-a-circle_icon-icons.com_56445.png";
          
          
          this.nodes["5"] = {name: "Database Endpoint", size: 16, theme: this.theme, nodeData: device, image: networkImage , ip: ip};
        
        }else if (deviceName.includes("iDRAC")){
          deviceName = "System Manager";
          url = "https://static.vecteezy.com/system/resources/previews/009/781/517/non_2x/gear-inside-laptop-icon-of-system-management-vector.jpg";
          continue;
        }else{
          deviceName = "Sensor";
          url = "https://cdn-icons-png.freepik.com/256/15038/15038808.png";
          continue;
        }
        

        if (deviceName in seenDevicesNames){
          seenDevicesNames[deviceName] += 1;
        }else{
          seenDevicesNames[deviceName] = 1;
        }
        let storageName = `${ip} ${deviceName} ${seenDevicesNames[deviceName]}`;

        
        

        if (deviceName == "Database"){
          this.nodes["database Hub"] = {name: "Database Connector", size: 16, theme: this.theme, nodeData: device, image: "https://cdn-icons-png.flaticon.com/512/432/432545.png" , ip: ip};
          this.edges["database Hub Connection"] = {source: "database Hub", target: ip, nodeData: USBs[device], color:  "#062236", ip: ip}
          
          let networkImage = "https://cdn.icon-icons.com/icons2/614/PNG/512/wifi-symbol-inside-a-circle_icon-icons.com_56445.png";
          for (let i = 0; i < 3; i++){
            this.nodes["database" + i] = {name: "Database", size: size, theme: this.theme, nodeData: device, image: url , ip: ip};
            this.edges["databaseConnection" + i] = {source: "database Hub", target: "database" + i, nodeData: USBs[device], color:  "#062236", ip: ip}
            

            this.nodes["5" + i] = {name: "Database Endpoint", size: 16, theme: this.theme, nodeData: device, image: networkImage , ip: ip};
            this.edges["6" + i] = {source: "5" + i, target: "database" + i, nodeData: {}, color:  "#062236", ip: ip}

          }
          
          this.edges["6"] = {source: "5", target: storageName, nodeData: {}, color:  "#062236", ip: ip}

          this.nodes[storageName] = {name: deviceName, size: size, theme: this.theme, nodeData: device, image: url , ip: ip};
          this.edges[storageName] = {source: "database Hub", target: storageName, nodeData: USBs[device], color:  "#062236", ip: ip}

          
        }else{
          // Old Color: ADD8E6
          this.nodes[storageName] = {name: deviceName, size: size, theme: this.theme, nodeData: device, image: url , ip: ip};
          this.edges[storageName] = {source: ip, target: storageName, nodeData: USBs[device], color:  "#062236", ip: ip}
        }
        
        // Deciding Positioning
        if (!(storageName in this.layouts["nodes"])){
          let angle = Math.random() * 2 * Math.PI;
          let x = this.radius / 4 * Math.cos(angle);
          let y = this.radius / 4 * Math.sin(angle);

          this.layouts["nodes"][storageName] = {x: this.layouts["nodes"][ip].x + x, y: this.layouts["nodes"][ip].y + y}
        }

          
        
      

      }
  },
  renderNetwork(networks, ip){
    if (ip.includes("172.20.88.17")) return;

    for (const networkIndex in networks){
        continue;
        let network = networks[networkIndex];
        let networkName = network["Interface Name"] 

        let nodeData = {};
        nodeData["Device Descriptor"] = {"Device Class": networkName}

        
        for (const attribute in network){
          nodeData["Device Descriptor"][attribute] = network[attribute];
        }

        

        
        networkName = `Network: ${networkName}`;
        


        // Old color: #6C6C6C
        // Make repeating nodes separate besides for the lo network
        if (networkName.includes("lo")){
          this.nodes["Connective Network"] = {name: "", size: 12, theme: this.theme, nodeData: nodeData, image: "https://www.svgrepo.com/show/61290/wifi-logo.svg"}
          this.edges[networkName + Math.random()] = {source: "Connective Network", target: ip, color: "#323832", ip: ip}
        }else{
          let networkImage = "https://cdn.icon-icons.com/icons2/614/PNG/512/wifi-symbol-inside-a-circle_icon-icons.com_56445.png";
          this.nodes[networkName + ip] = {name: "Network", size: 12, theme: this.theme, nodeData: nodeData, image: networkImage, ip: ip}
          this.edges[networkName + Math.random()] = {source: networkName + ip, target: ip, color: "#323832", ip: ip}

            if (!this.networkNames.includes(networkName + ip)){
            this.networkNames.push(networkName + ip)
          }
        }
        

        // Deciding Positioning
        if (!(networkName + ip in this.layouts["nodes"])){
          let angle = Math.random() * 2 * Math.PI;
          let x = this.radius / 2 * Math.cos(angle);
          let y = this.radius / 2 * Math.sin(angle);

          this.layouts["nodes"][networkName + ip] = {x: this.layouts["nodes"][ip].x + x, y: y + this.layouts["nodes"][ip].y}
        }

    
      }
  }, 
  renderPackages(packages, ip){
    if (ip.includes("172.20.88.17")) return;
    let nodeData = {};
    nodeData["Device Descriptor"] = {"Device Class": "Packages"}
    this.packagesNames.push("Packages")


    for (const packageName in packages){
      nodeData["Device Descriptor"][packageName] = packages[packageName];
    }
    
    this.nodes["Packages" + ip] = {name: "Packages", size: 12, theme: this.theme, nodeData: nodeData, image: "https://cdn0.iconfinder.com/data/icons/flatt3d-icon-pack/512/Flatt3d-Box-512.png", ip: ip}
    this.edges["Packages" + Math.random()] = {source: "Packages" + ip, target: ip, color: "#323832", ip: ip}
  
    // Deciding Positioning
    if (!("Packages" + ip in this.layouts["nodes"])){
      let angle = Math.random() * 2 * Math.PI;
      let x = this.radius / 8 * Math.cos(angle);
      let y = this.radius / 8 * Math.sin(angle);

      this.layouts["nodes"]["Packages" + ip] = {x: this.layouts["nodes"][ip].x + x, y: this.layouts["nodes"][ip].y + y}
    }
      
  },
  renderAddedPackages(addedPackages, ip, startDate){
    if ( ip.includes("172.20.88.17")) return;
    if (Object.keys(addedPackages).length > 3){
        let nodeData = {};
        nodeData["Device Descriptor"] = {"Device Class": "Added Packages"}
        this.packagesNames.push("Added Packages")


        for (const packageName in addedPackages){
          nodeData["Device Descriptor"][packageName] = addedPackages[packageName];
        }
        
        this.nodes["Added Packages" + ip] = {name: "Added Packages", theme: this.theme, size: 12, nodeData: nodeData, image: "https://cdn0.iconfinder.com/data/icons/flatt3d-icon-pack/512/Flatt3d-Box-512.png", ip: ip}
        this.edges["Added Packages" + Math.random()] = {source: "Added Packages" + ip, target: "Packages" + ip, color: "#0c4f09", ip: ip}
      
        // Deciding Positioning
        if (!("Added Packages" + ip in this.layouts["nodes"])){
          let angle = Math.random() * 2 * Math.PI;
          let x = this.radius / 8 * Math.cos(angle);
          let y = this.radius / 8 * Math.sin(angle);

          this.layouts["nodes"]["Added Packages" + ip] = {x: this.layouts["nodes"][ip].x + x, y: this.layouts["nodes"][ip].y + y}
        }
      
      }else{
        for (let packageName in addedPackages){
          let nodeData = {};
          nodeData["Device Descriptor"] = {"Device Class": packageName}
          nodeData["Device Descriptor"]["Type"] = "Added Package";

          
          let packageSize = 12;
          let deviceImage = "https://cdn0.iconfinder.com/data/icons/flatt3d-icon-pack/512/Flatt3d-Box-512.png";
          let nodeLabel = undefined;
          if (packageName.includes("malicious")){

            nodeLabel = true;
            packageSize = 29;
            if (packageName.includes("2")) continue; // Dont process second malicious package

            deviceImage = "https://cdn-icons-png.flaticon.com/512/8339/8339318.png";
            packageName = "Malicious Software Package";
          
            if (this.maliciousPackageNotificationSent == 0){
              this.maliciousPackageNotificationSent = 1;
              this.$emit("newNotification", {key: this.formatDate(new Date(startDate)), value: "Malicious Package Detected @ IP 192.168.1.26"});
            }
            
            
          }

          if (!this.packagesNames.includes(packageName)){
            this.packagesNames.push(packageName)
          }

          this.nodes[packageName + ip] = {name: packageName, theme: this.theme,  label: nodeLabel, size: packageSize,nodeData: nodeData, image: deviceImage, ip: ip}
          this.edges[packageName + Math.random()] = {source: packageName + ip, target: "Packages" + ip, color:  "#0c4f09" , ip: ip}
        
          // Deciding Positioning
          if (!(packageName + ip in this.layouts["nodes"])){
            let angle = Math.random() * 2 * Math.PI;
            let x = this.radius / 8 * Math.cos(angle);
            let y = this.radius / 8 * Math.sin(angle);

            this.layouts["nodes"][packageName + ip] = {x: this.layouts["nodes"][ip].x + x, y: this.layouts["nodes"][ip].y + y}
          }
        }
      }
  },
  renderRemovedPackages(removedPackages, ip){
    if (ip.includes("172.20.88.17")) return;
    if (Object.keys(removedPackages).length > 3){
        let nodeData = {};
        nodeData["Device Descriptor"] = {"Device Class": "Removed Packages"}
        this.packagesNames.push("Removed Packages")


        for (const packageName in removedPackages){
          nodeData["Device Descriptor"][packageName] = removedPackages[packageName];
        }
        
        this.nodes["Removed Packages" + ip] = {name: "Removed Packages", theme: this.theme, size: 12, nodeData: nodeData, image: "https://cdn0.iconfinder.com/data/icons/flatt3d-icon-pack/512/Flatt3d-Box-512.png", ip: ip}
        this.edges["Removed Packages" + Math.random()] = {source: "Removed Packages" + ip, target: "Packages" + ip, color: "#4f0e09", ip: ip}
      
        // Deciding Positioning
        if (!("Removed Packages" + ip in this.layouts["nodes"])){
          let angle = Math.random() * 2 * Math.PI;
          let x = this.radius / 8 * Math.cos(angle);
          let y = this.radius / 8 * Math.sin(angle);

          this.layouts["nodes"]["Removed Packages" + ip] = {x: this.layouts["nodes"][ip].x + x, y: y + this.layouts["nodes"][ip].y}
        }
      }else{
        for (let packageName in removedPackages){

          let nodeData = {};
          nodeData["Device Descriptor"] = {"Device Class": packageName}
          nodeData["Device Descriptor"]["Version"] = removedPackages[packageName];

          

        
          let packageSize = 12;
          let nodeLabel = undefined;
          let deviceImage = "https://cdn0.iconfinder.com/data/icons/flatt3d-icon-pack/512/Flatt3d-Box-512.png";
          if (packageName.includes("malicious")){

            nodeLabel = true;
            packageSize = 29;
  

            if (packageName.includes("2")) continue; // Dont process second malicious package
            deviceImage = "https://cdn-icons-png.flaticon.com/512/8339/8339318.png";
            packageName = "Malicious Software Package";
          }

          if (!this.packagesNames.includes(packageName)){
            this.packagesNames.push(packageName)
          }

          this.nodes[packageName + ip] = {name: packageName, theme: this.theme,  label: nodeLabel, size: packageSize,nodeData: nodeData, image: deviceImage, ip: ip}
          this.edges[packageName + Math.random()] = {source: packageName + ip, target: "Packages" + ip, color: "#4f0e09" , ip: ip}
        
          // Deciding Positioning
          if (!(packageName + ip in this.layouts["nodes"])){
            let angle = Math.random() * 2 * Math.PI;
            let x = this.radius / 8 * Math.cos(angle);
            let y = this.radius / 8 * Math.sin(angle);

            this.layouts["nodes"][packageName + ip] = {x: x + this.layouts["nodes"][ip].x, y: y + this.layouts["nodes"][ip].y}
          }
        }
      }
  },
  renderDevice(device){
    // Takes a node individually and renders every single connected to it. 
    let entry = device;
    let [startDate, endDate, ip, deviceData, packages, addedPackages, removedPackages] = [entry["startDate"], entry["endDate"], entry["ip"], entry["entry"], entry["Packages"], entry["addedPackages"], entry["removedPackages"]]; 


    
    if (startDate <= Date.parse(this.date)  && Date.parse(this.date) <= endDate){
      this.renderMachineNode(device, ip);
    
      this.renderUSBs(deviceData["USB Devices"], ip, startDate);

      this.renderNetwork(deviceData["Network Interfaces"], ip);

      this.renderPackages(packages, ip, startDate);
      this.renderAddedPackages(addedPackages, ip, startDate);
      this.renderRemovedPackages(removedPackages, ip);
      
    }

  },
  renderIP(ip){
    if (ip.includes("172.20.88.17")) return;
    // Delete all old nodes on the ip
    for (const nodeName of Object.keys(this.nodes)){
      let node = this.nodes[nodeName];

      if (node.ip == ip){
        delete this.nodes[nodeName];
      }

    }

    for (const edgeName of Object.keys(this.edges)){
      let edge = this.edges[edgeName];

      if (edge.ip == ip){
        delete this.edges[edgeName];
      }
    }

    let deviceToRender = undefined;
    for (const device of this.devices){

      if (device["ip"] == ip && device["startDate"] < this.date){
        deviceToRender = device;
      }

      if (device["startDate"] > this.date){
        break
      }
    }

    this.renderDevice(deviceToRender);


  },
  visualUpdateMaliciousNode(){

    let nodeNames = ["192.168.1.134 Malicious Boson Camera 1", "Malicious Software Package192.168.1.26"]
    for (const nodeName of nodeNames){
 
      if (nodeName in this.nodes){
      let currentSize = this.nodes[nodeName].size;


      if (currentSize < 30){
        this.ascending = true;
        this.nodes[nodeName].size += 3;
      }else if (currentSize < 60){

        if (this.ascending){
          this.nodes[nodeName].size += 2;
        }else{
          this.nodes[nodeName].size -= 2;
        }

      }else{
        this.ascending = false;
        this.nodes[nodeName].size -= 3;
      }
   
      
    }
    }
    
  },
    updateDevices(){

        this.visualUpdateMaliciousNode(); // Just for the demo some visual effects when the malicious package comes into show

        if (this.lastDate == undefined){
          for (const index in this.devices){
            this.renderDevice(this.devices[index]);
          }
        }else{


          let timestamps = Object.keys(this.timestamps);
          let currentDate = this.date.getTime();
          let pastDate = this.lastDate.getTime();
          let ips_to_render = [];

          for (let i = 0; i < timestamps.length; i++){
            let timestamp = timestamps[i];

            // If you either went past a timestamp either forward or backwards
            if (this.prevTheme != this.theme || (pastDate <= timestamp && timestamp <= currentDate) || (currentDate <= timestamp && timestamp <= pastDate)){
              for (let i = 0; i < this.timestamps[timestamp].length; i++){
                let ip = this.timestamps[timestamp][i];

                if (!(ips_to_render.includes(ip))){
                  ips_to_render.push(this.timestamps[timestamp][i]);
                }
              }
              
            }
          }



          if (ips_to_render.length > 0){
            
            for (const ip of ips_to_render){
              this.renderIP(ip);
            }
          }

        }


        this.lastDate = this.date
        this.prevTheme = this.theme;

    }
  }
}
</script>


<template>
  <div id="container-graph">

          <v-network-graph
            class="graph"
            v-model:nodes="nodes"
            :edges="edges"
            :configs="configs"
            v-model:layouts="layouts"
            v-model:selected-nodes="selectedNodes"
            ref='graph'
          >

          <defs>
              <!--
                Define the path for clipping the face image.
                To change the size of the applied node as it changes,
                add the `clipPathUnits="objectBoundingBox"` attribute
                and specify the relative size (0.0~1.0).
              -->
              <clipPath id="faceCircle" clipPathUnits="objectBoundingBox">
                <circle cx="0.5" cy="0.5" r="0.5" />
              </clipPath>
            </defs>

            <!-- Replace the node component -->
            <template #override-node="{ nodeId, scale, config, ...slotProps }">
              <!-- circle for filling background -->
              <circle
                class="face-circle"
                :r="config.radius * (scale - 0.1)"
                fill="#ffffff"
                v-bind="slotProps"
              />
              <!--
                The base position of the <image /> is top left. The node's
                center should be (0,0), so slide it by specifying x and y.
              -->
              <image
                class="face-picture"
                :x="-config.radius * (scale - 0.1)"
                :y="-config.radius * (scale - 0.1)"
                :width="config.radius * (scale - 0.1) * 2"
                :height="config.radius * (scale - 0.1) * 2"
                :xlink:href="`${nodes[nodeId].image}`"
                clip-path="url(#faceCircle)"
              />
              <!-- circle for drawing stroke -->
              <circle
                class="face-circle"
                :r="config.radius * (scale - 0.1)"
                fill="none"
                stroke="#808080"
                :stroke-width="1 * (scale - 0.1)"
                v-bind="slotProps"
              />
            </template>

          </v-network-graph>

  
  </div>
  

</template>

<style scoped>

#container-graph{
    height: 100%;
    width: 100%;

}

.face-circle,
.face-picture {
  transition: all 0.1s linear;
}

.face-picture {
  pointer-events: none;
}


</style>