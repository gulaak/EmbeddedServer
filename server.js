const express = require('express')
const app = express()
const mongoose = require('mongoose')
const { PORT, mongoUri } = require('./config')
const cors = require('cors')
const morgan = require('morgan')
const bodyParser = require('body-parser')

//const userItemRoutes = require('./routes/api/UserItems')
//const uploadFileRoutes = require('./routes/api/file');
const path = require('path')

app.use(cors())
app.use(morgan('tiny'))
app.use(bodyParser.json())


const PeripheralModel = require('./models/PeripheralModel'); // grab data base model
const { delimiter } = require('path')
const { isDeepStrictEqual } = require('util')



// mongoose.connect(mongoUri, {
//     useNewUrlParser: true,
//     useCreateIndex: true,
//     useUnifiedTopology: true,
//     useFindAndModify: false

// }).then(()=> console.log('MongoDB database Connected'))
//   .catch((err)=> console.log(err));

//app.use('/api/UserItems', userItemRoutes);
//app.use('/api/file', uploadFileRoutes);
  
// app.get('/', (req,res)=>{
//     res.send("Hello World");
// });

var server = app.listen(5000, ()=>{ console.log(`Server Started Listening on ${PORT}`)});




//var server = app.listen(PORT, ()=>{ console.log(`Server Started Listening on ${PORT}`)});


var state = {
  UART1: [false,0,[]],
  UART4: [false,0,[]],
  I2C: [false,0,[]],
  SPI: [false,0,[]],
  GPIO_49:[false,0,[]],
  GPIO_60:[false,0,[]],
  GPIO_117:[false,0,[]],
  GPIO_115:[false,0,[]],
  GPIO_112:[false,0,[]],
  GPIO_20:[false,0,[]],
  GPIO_66:[false,0,[]],
  GPIO_69:[false,0,[]],
  GPIO_45:[false,0,[]],
  GPIO_47:[false,0,[]],
  GPIO_27:[false,0,[]],
  GPIO_67:[false,0,[]],
  GPIO_68:[false,0,[]],
  GPIO_44:[false,0,[]],
  GPIO_26:[false,0,[]],
  GPIO_46:[false,0,[]],
  GPIO_65:[false,0,[]],
  GPIO_61:[false,0,[]],
  PWM1A:[false,0,[]],
  PWM1B:[false,0,[]],
  PWM2A:[false,0,[]],
  PWM2B:[false,0,[]],
  AIN0:[false,0,[]],
  AIN1:[false,0,[]],
  AIN2:[false,0,[]],
  AIN3:[false,0,[]],
  AIN4:[false,0,[]],
  AIN5:[false,0,[]],
  AIN6:[false,0,[]]
};

const db_id = "5fa0ad64449b780963d4badb";

async function add_new_item(){
  
  var new_item = await PeripheralModel.findByIdAndUpdate(db_id, x );
  //console.log("New Item " + new_item)
}

//add_new_item();

var io = require('socket.io')(server);
io.sockets.on('connection', newConnection);

function newConnection(socket){

  io.to(socket.id).emit("peripheral status", state) // give client peripheral state

  socket.on('release', (ID)=>{
    //releaseResource(ID); // releases resource requested by the client user (client must ) - releaseResource notifies the embedded device 
    io.sockets.emit("stop program", ID);
  });
  
  socket.on('update stats', (data) => {

    io.sockets.emit("cpu stats",data)
    
    
  });

  socket.on('release beaglebone', (data) => {
    //console.log("received beaglebone signal")
    releaseResource(data[2],data[1]) // release resources from client
  });

  socket.on('clear queue', deleteQueue);

  socket.on('file message', (data,ID) =>{
    handleFile(data,ID)
  });
  socket.on('std out', (payload)=>{io.to(payload[1]).emit("update text",payload[0]); }); //releaseResource(payload[1])});
  socket.on('compile error', (payload)=> { io.to(payload[1]).emit("compile error", payload[0] ) ; releaseResource(payload[2],payload[1])}); // Compile Failed
  //socket.on('compile success', (ID)=> { io.to(ID).emit("compile success"); //console.log("Compile Success")}); // Compile Worked and Is running on device
  // update state of database for usage of ports
}

function notifyUsers(new_item){
  //console.log("Done with async call");  
  io.sockets.emit('peripheral status', new_item[0].toObject());
  //io.sockets.emit("send file", new_item[2], new_item[1]); // BeagleBone will be only client listening to this (Must track ID of socket)
}

function notifyUser(new_item){
  io.to(new_item[1]).emit("peripheral status", new_item[0].toObject());

}



function deleteQueue(queue_obj){
  //console.log(queue_obj)
  for( var key in queue_obj ) {
    if( key != "program" &&  key != "ID"){ // means this is a resource key
      for( let [idx , entry ] of state[key][2].entries()){ // iterate over all waiting processes in queue
        if(isDeepStrictEqual(entry,queue_obj)){ // this needs to be deleted
          state[key][2].splice(idx,1); // remove element from array
          return;
        }
      }
    }
  }
}


var id_map = {} // map that shows which ID holds what resource
var running = {} // map that shows which ID is running 

function mergeKeys(srcobj,dstobj){ // merge keys in per socket ID

  for( var key in dstobj){
      if ( srcobj[key] == undefined){
        srcobj[key] = dstobj[key]
      }else{
        srcobj[key][1]++;
      }
  }
  return srcobj;
}

function handleFile(data,ID){
  // console.log(data);
  // console.log(ID);
  // console.log(data.split('\n'))
  let new_entry = extract_peripherals(data.split('\n')); // send array of lines
  //file parsing will need to handle gerneation of new_entry;
  var failed = false;
  for( var item in new_entry){ // iterate over keys of peripherals program wants to control
    var query = ""
    try {
      query = state[item][0];
    } catch(err){
      continue;
    }
    if(query == true){ 
      new_entry["program"] = data // put program into the new_entry
      new_entry["ID"] = ID
      state[item][2].push(new_entry)  // peripheral utilized 
      failed = true

      
    }
  }
  if( failed ){
    io.to(ID).emit("queue add", new_entry)
    return;
  } 
  //new_entry = {uart1: [true,0], uart4: [true, 0]};
  // console.log("New Entry")
  // console.log(new_entry);
  // try{
  //   console.log("Old Entry")
  //   console.log(id_map[ID])
  //   new_obj = mergeKeys(id_map[ID],new_entry);
  //   console.log("new Object")
  //   console.log(new_obj)
  //   id_map[ID] = new_obj;
  // } catch(err){
  //   id_map[ID] = new_entry;
  // }
  // console.log(id_map[ID])
  
  running[ID] = true
  updateState(new_entry, true)
  //console.log(state)
  io.sockets.emit('peripheral status', state ); // update all clients
  io.sockets.emit('send program', data, ID, new_entry);
}

function releaseResource(peripherals,ID){ // when we release a resource we try to dispatch any programs that is waiting for that resource
  // var peripherals = ""
  // try { 
  //   peripherals = id_map[ID]; // get the peripherals associated with this socket ID
  // }
  // catch(err){
  //   return; // that ID doesnt have any peripherals ( nothin needs to be done )
  // }

 // console.log(peripherals)
  running[ID] = false
  new_resource_map = {}
  updateState(peripherals, false) // release all peripherals acording to this socket ID 
  for(var item in peripherals){
    if( state[item][2].length == 0){ // nothing is waiting
      continue;
    } else { // entries are waiting evaluate them in a fifo manner
      entry_num = 0;
      for( var entry of state[item][2]){
        valid = true;
        map = {}
        for( var key in entry){ // check if all other peripherals are available
          if(key == "program" || key == "ID")continue; // disregard program key and socket ID
          if(state[key][0]== true){
            valid = false; // cannot dispatch
            break;
          }
          map[key] = entry[key]
        }
        if(valid && !running[entry["ID"]]){
          new_resource_map = {...new_resource_map, ...map}
          //console.log("New Resource Map")
          //console.log(new_resource_map)
          io.sockets.emit("send program",entry["program"],entry["ID"],new_resource_map) // dispatch program to BeagleBone 
          running[entry["ID"]] = true // now running 
          id_map[entry["ID"]] = new_resource_map;
          state[item][2].splice(entry_num,1) // remove the element
          io.to(entry["ID"]).emit('dispatch queue', entry["program"]); // tell client that their program is dispatched ß
        }
        entry_num++
      }
    }
  }
  if( Object.keys(new_resource_map).length != 0){ // if we dispatch new processes ( update state table )
    updateState(new_resource_map,true)
    
  }
  io.sockets.emit("peripheral status",state) // update global peripheral state 
 

}

function updateState(resource_map, update_state){
  for(var key in resource_map){
    if( (key.match("GPIO") && resource_map[key][0]) || key.match("PWM") ){
      state[key][0] = update_state
     
    }
    if( !update_state){
      state[key][0] = update_state // peripheral is now used
      state[key][1] = state[key][1] - resource_map[key][1]
    } else{
      state[key][1] = state[key][1] + 1
    }
  }
}


function extract_peripherals(line_array){
  var collection  = [ "GPIO(", "UART(", "I2C(", "SPI(", "PWM(", "ADC(" ]
  var peripherals = {}
  for( var line of line_array){

    var newLine = line.split(' ').join(''); // get rid of all spaces

    for( var delim of collection){
      var status = ""

      if(delim == "GPIO("){
        status = extract_first_two_args( newLine, delim );
 
        if( status.length > 0){
          key = delim.substring(0,delim.length-1) + "_" + status[0];
          peripherals[key] = [(status[1]=="1")? 1 : 0,1]; 
        }
      } 
      else{
        status = extract_first_arg( newLine , delim );
        if( status.length > 0){

          key = delim.substring(0,delim.length-1)
          if(delim == "UART("){
            key += status[0]
          }else if(delim == "PWM("){
            key += status[0].slice(1,status[0].length-1); // disregard quotes 
          }else if(delim == "ADC("){
            key = status[0].slice(1,status[0].length-1);
          }
          peripherals[key] = [0,1]
        }
      }
    }
  }

  return peripherals;
}

function extract_first_two_args ( newLine , delimiter_string  ){
  if ( !newLine.includes(delimiter_string)){
    return false
  } else {
    first_arg = newLine.split('(').pop().split(',')[0]
    second_arg = newLine.split(',').pop().split(')')[0]
    if ( second_arg.split(',').length > 1){
      second_arg = newLine.split(',').pop().split(',')[0]
      return [first_arg, second_arg ]
    } else{
      return [first_arg, second_arg ]
    }
  }
}

function extract_first_arg(newLine , delimiter_string ){
  if ( !newLine.includes(delimiter_string)){
    return false
  } else {
    first_arg = newLine.split('(').pop().split(')')[0]

    if( first_arg.split(',').length > 1){
      first_arg = newLine.split('(').pop().split(',')[0]
      return [first_arg , 0]
    } else{
      return [first_arg,0];
    }
  }
}

