// Configuration for IPFS instance
const ipfsConfig = {
  preload: { enabled: false }, // Prevents large data transfers
  repo: '/orbitdb/examples/todomvc/ipfs/0.27.0',
  EXPERIMENTAL: {
    pubsub: true,
  },
  config: {
    Addresses: {
      Swarm: [
        // Use IPFS dev signal server
        // Websocket:
        // '/dns4/ws-star-signal-1.servep2p.com/tcp/443/wss/p2p-websocket-star',
        // '/dns4/ws-star-signal-2.servep2p.com/tcp/443/wss/p2p-websocket-star',
        // '/dns4/ws-star.discovery.libp2p.io/tcp/443/wss/p2p-websocket-star',
        // WebRTC:
        // '/dns4/star-signal.cloud.ipfs.team/wss/p2p-webrtc-star',
        '/dns4/wrtc-star1.par.dwebops.pub/tcp/443/wss/p2p-webrtc-star/',
        '/dns4/wrtc-star2.sjc.dwebops.pub/tcp/443/wss/p2p-webrtc-star/',
        '/dns4/webrtc-star.discovery.libp2p.io/tcp/443/wss/p2p-webrtc-star/',
        // Use local signal server
        // '/ip4/0.0.0.0/tcp/9090/wss/p2p-webrtc-star',
      ]
    },
  }
}

// Configuration for the database
const dbConfig = {
  // If database doesn't exist, create it
  create: true,
  // Don't wait to load from the network
  sync: false,
  // Load only the local version of the database
  // localOnly: true,
  // Allow anyone to write to the database,
  // otherwise only the creator of the database can write
  accessController: {
    write: ['*'],
  }
}

const store = async (name) => {
  // Create IPFS instance
  const ipfs = await Ipfs.create(ipfsConfig)
  // Create an OrbitDB instance
  const orbitdb = await OrbitDB.createInstance(ipfs)
  // Open (or create) database
  const db = await orbitdb.docstore(name, dbConfig)
  // Done
  return db
}
