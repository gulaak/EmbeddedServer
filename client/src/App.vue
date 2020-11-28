<template>
  <div id="app">


    <b-form-file
      v-model="file1"
      :state="Boolean(file1)"
      placeholder="Choose a file or drop it here..."
      drop-placeholder="Drop file here..."
    ></b-form-file>
    <div class="mt-3"> 
      <b-button @click="open_text=true" variant="outline-primary" > Manual Entry </b-button>
      <b-button @click="file_send()" variant="outline-primary"> Submit </b-button>
      <b-button @click="release_request()" variant="outline-primary"> Release </b-button>
      <span > Compile Status : <span v-bind:class="{ fail : compileStatus=='Error' , success: compileStatus=='Success'}" > {{compileStatus}} </span> </span>
    </div>
     <!-- <h1 v-for="(value, name ) in items" v-bind:key="value" >
        {{ name }} : {{ value }}
      </h1> -->

    <vue-modaltor
      :visible="open"
      @hide="open = false">
        <p>
        {{ program_data }}
        </p>
    </vue-modaltor>

    <vue-modaltor
      :visible="open_text"
      @hide="open_text = false">
      <b-container>
        <b-row>
          <b-form-textarea
            id="textarea"
            @keydown.tab.prevent="tabber($event)"
            v-model="modal_text"
            placeholder="Enter Python Program..."
            rows="15"
            max-rows="15">
          </b-form-textarea>
        </b-row >
        <b-row style="height:10px">
        </b-row>
        <b-row>
          <b-button variant="outline-primary" @click="file_send_modal()"> Submit! </b-button>
        </b-row>
      </b-container>
    </vue-modaltor>



    
    <div class="mt-3" v-for="(row,idx_row) of queue2D" :key="row">
        <b-card-group deck>
        <b-card class="text-center" v-for="(column, idx_col) of row" :key="column">
            <b-card-text > 
                  <button  @click="open = true ; moreInfo(idx_row * 3 + idx_col)" style="border: None">
                    <b-icon icon="exclamation-circle-fill" variant="info" scale="1"></b-icon>
                  </button>
                  <button @click="clearQueue(idx_row * 3 + idx_col)" style="border: None">
                    <b-icon icon="x-circle" scale="1" variant="danger"></b-icon>
                  </button>

            </b-card-text>
        </b-card>
        </b-card-group>
    </div>

      <div class="mt-3" v-for="item of peripheral2D" v-bind:key="item">
      <b-card-group deck>
          <b-card class="text-center" v-bind:class="{ occupied: column[1],  used: (column[2] > 0 && !column[1]) , free: column[2]==0  }" v-for="column of item" v-bind:key="column"> 
              <b-card-text >{{ column[0]}} {{ column[2]}}</b-card-text>
          </b-card> 
      </b-card-group>
      </div>
      <div class="mt-3" >
       <b-card-group deck>
        <b-card class="text-center" :class="{ occupied: (stats[0] > 50 && stats[0] <=100)}"  v-for="stats of util" :key="stats">
              <b-card-text> {{ stats[1] }}</b-card-text>
              <b-card-text> {{ stats[0] }}</b-card-text>
         </b-card>
      </b-card-group>
      </div>
      <div class="mt-3">
      <b-card> 
        <b-card-text class="text-center">Std Out </b-card-text>
      </b-card>
      <b-list-group>
        <b-list-group-item v-for="entry of stdout_list" v-bind:key="entry"> <span style="color: blue">[{{entry[1]}}]</span> <span style="width:1.5em"> </span>  {{entry[0]}}</b-list-group-item>
      </b-list-group>
      </div>

     
  
  </div>

</template>

<script>
import io from "socket.io-client"

export default {
  name: "App",
  data() {
    return {
      file1:"",
      description: "",
      editedDescription: "",
      selected: {},
      socket: "",
      compileStatus: "",
      peripheral2D: "",
      stdout_list: [],
      status: {}, 
      queue: [],
      queue2D: "",
      program_data:"",
      open: false,
      modal_text: "",
      open_text: false,
      util: []
    };
  },


  mounted(){
    this.socket = io.connect('http://bc614e814241.ngrok.io')
    //this.socket = io.connect('http://10.0.0.72:5000')
    this.socket.on("peripheral status", (data) => { // update all the peripheral statuses 
      console.log("In status")
      console.log(data)  
      this.peripheral2D = this.convertObjectTo2D(data,3);
    });

    this.socket.on("queue add", (data) =>{
      this.queue.push(data);
      console.log(data)
      this.queue2D = this.convertTo2D(this.queue,3);
    });

    this.socket.on("cpu stats", (data) => { // update all the peripheral statuses 
      var temp = []
      for(var i = 0 ; i < 4 ; ++i){ // loop over all data ( cpu util , available memory, used memory, percentage memory used)
        switch(i){
          case 0: temp[i] = [data[i],"CPU"]; break;
          case 1: temp[i] = [data[i],"Avail"]; break;
          case 2: temp[i] = [data[i],"Used"]; break;
          default: temp[i] = [data[i],"Perc"]; break;
        }
        
      }
      this.util = temp 
    });


    this.socket.on("update text", (data)=>{
      this.compileStatus= "Success"
      var time_obj = new Date()
      var timestamp = time_obj.getHours() + ":" + time_obj.getMinutes() + ":" + time_obj.getSeconds()
      this.stdout_list.push([data, timestamp])
      if ( this.stdout_list.length > 6){
        this.stdout_list.shift();
      }
    })
    this.socket.on("compile success", ()=>{this.compileStatus = "Success"});

    this.socket.on("compile error", (data)=>{
      this.compileStatus = "Error";
      var time_obj = new Date()
      var timestamp = time_obj.getHours() + ":" + time_obj.getMinutes() + ":" + time_obj.getSeconds()
      this.stdout_list.push([data, timestamp])

    });

    this.socket.on("dispatch queue", (program_string) => {
      console.log("dispatched")
      for ( let [idx, item] of this.queue.entries()){
        if(item["program"] === program_string){
          this.queue.splice(idx,1);
          break;
        }
      }
      this.queue2D = this.convertTo2D(this.queue,3); // render to UIß
    });



    //this.peripheral2D = this.convertObjectTo2D(this.items,3);
  },


  methods: {

    file_send(){
      //var file = document.getElementById("fileForUpload").files[0]
      //console.log(file)
      if(this.file1){
        var reader = new FileReader();
        reader.readAsText(this.file1,"UTF-8");
        var socket = this.socket
        reader.onload = function(evt){
          console.log(evt.target.result)
          console.log(socket)
          for(var i = 0; i < 100; ++i){
            socket.emit('file message', evt.target.result, socket.id); // send socket ID to track which client sent a file.
          }
        }
      }
      
    },

    tabber (event) {
        let text = this.modal_text,
          originalSelectionStart = event.target.selectionStart,
          textStart = text.slice(0, originalSelectionStart),
          textEnd =  text.slice(originalSelectionStart);

        this.modal_text = `${textStart}\t${textEnd}`
        event.target.value = this.modal_text // required to make the cursor stay in place.
        event.target.selectionEnd = event.target.selectionStart = originalSelectionStart + 1
    },

    moreInfo(idx){
      console.log("Index: " + idx)
      this.program_data = this.queue[idx]["program"]
    },


    file_send_modal(){
     // for(var i = 0; i < 100 ; ++i){
        this.socket.emit('file message', this.modal_text, this.socket.id); // send program from modal to backend to program
      //}
      this.open_text = false
    },

    release_request(){
      this.socket.emit('release', this.socket.id); // release any resources I am holding. 
    },

    clearQueue(id){
      console.log("Clear Queue")
      let queue_obj = this.queue[id]
      this.queue.splice(id,1)
      this.queue2D = this.convertTo2D(this.queue,3);
      console.log(this.queue2D)
      this.socket.emit('clear queue', queue_obj);
      
    },

    handleResponse(data){
      this.status = data; // data is an object that 
    },

    convertTo2D(array,numOfRows){
      var temp = []
      var j = 0
      for( var i = 0 ; i < array.length ; ++i){
        if (i % numOfRows == 0){
          temp.push( [] )
          if( i != 0){
            j+=1
          }
          temp[j].push(array[i])
        } else{
          temp[j].push(array[i])
        }
      }
      console.log(temp)
      return temp
    },

    convertObjectTo2D(object,numOfRows){ // break an object into a 2D array to display in UI grid 
      var i = 0;
      var j = 0;
      var temp = []
      
      console.log(object)
      for( const key in object){
        if (key == "_id" || key == "__v") continue; 
        console.log(key)
        if ( i % (numOfRows) == 0){
          temp.push([])
          if (i != 0){
            j +=1
          }
          temp[j].push([key,object[key][0],object[key][1]]);
          
        } else{
          temp[j].push([key,object[key][0],object[key][1]]);
        }
        ++i;
      }
     console.log(temp);
     return temp;
    }

  }
};
</script>

<style>
#app {
  margin: auto;
  margin-top: 3rem;
  max-width: 700px;
}
.icon {
  cursor: pointer;
}


.free {
  background-color: green;
  color: black;
}
.fail {
  color: red;
}
.success{
  color: green;
}
.occupied {
  background-color: red;
  color: black;
}

.used {
  background-color: yellow;
  color: black;
}

p {
    white-space: pre-wrap;
}

button {
  background: None;
}

b-row {
  padding-top: 10px;
  padding-bottom: 10px;
}







</style>
