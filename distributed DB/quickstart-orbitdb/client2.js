import { createOrbitDB } from '@orbitdb/core'
import { createLibp2p } from 'libp2p'
import { createHelia } from 'helia'
import { DefaultLibp2pOptions } from '@orbitdb/quickstart'

const libp2p = createLibp2p({ ...DefaultLibp2pOptions })
const ipfs = await createHelia({ libp2p })

const orbitdb = await createOrbitDB({ ipfs })

const db1 = await orbitdb.open('db1')
await db1.add('hello world 2!')
console.log(await db1.all())