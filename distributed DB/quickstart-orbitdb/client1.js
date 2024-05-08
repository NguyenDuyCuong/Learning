import { startOrbitDB, stopOrbitDB } from '@orbitdb/quickstart'

const orbitdb = await startOrbitDB()
const db1 = await orbitdb.open('db1')
await db1.add('hello world!')
console.log(await db1.all())
await stopOrbitDB(orbitdb)