from Converter import Converter
from Directory_Entry import Directory_Entry
from Mini_FAT import Mini_FAT
from Virtual_Disk import Virtual_Disk
from Directory import Directory
class File(Directory_Entry):
    content = ""
    parent = None

    def __init__(self, name, dirAttrib, dirFirstCluster, pa):
        Directory_Entry.__init__(self, name, dirAttrib, dirFirstCluster)
        if pa != None:
            self.parent = pa

    def GetMyDirectoryEntry(self):
        me = Directory_Entry(self.dir_name, self.dir_attr, self.dir_firstCluster)
        me.dir_empty = self.dir_empty
        me.dir_filesize = self.dir_filesize
        return me

    def GetMySizeOnDisk(self):
        size = 0
        if self.dir_firstCluster != 0:
            cluster = self.dir_firstCluster
            nextc = Mini_FAT.getClusterStatus(cluster)
            if cluster == 5 and nextc == 0:
                return size
            while cluster != -1:
                size += 1
                cluster = nextc
                if cluster != -1:
                    nextc = Mini_FAT.getClusterStatus(cluster)
        return size

    def EmptyMyClusters(self):
        if self.dir_firstCluster != 0:
            cluster = self.dir_firstCluster
            nextc = Mini_FAT.getClusterStatus(cluster)
            if cluster == 5 and nextc == 0:
                return
            while cluster != -1:
                Mini_FAT.setClusterStatus(cluster, 0)
                cluster = nextc
                if cluster != -1:
                    nextc = Mini_FAT.getClusterStatus(cluster)

    def WriteFileContent(self):
        me = self.GetMyDirectoryEntry()
        if (len(self.content) != 0):
            contentBytes = bytes(self.content, "utf-8")
            byteslst = Converter.splitBytes(contentBytes)
            clusterFatIndex = -1
            if (self.dir_firstCluster != 0):
                clusterFatIndex = Mini_FAT.getAvilableCluster()
                self.dir_firstCluster = clusterFatIndex
            else:
                clusterFatIndex = Mini_FAT.getAvilableCluster()
                if (clusterFatIndex != -1):
                    self.dir_firstCluster = clusterFatIndex

            lastCluster = -1
            for i in range(0, len(byteslst)):
                if (clusterFatIndex != -1):
                    Virtual_Disk.writeCluster(byteslst[i], clusterFatIndex)
                    Mini_FAT.setClusterStatus(clusterFatIndex, -1)
                    if (lastCluster != -1):
                        Mini_FAT.setClusterStatus(lastCluster, clusterFatIndex)
                    lastCluster = clusterFatIndex
                    clusterFatIndex = Mini_FAT.getAvilableCluster()
            if (len(self.content) == 0):
                if (self.dir_firstCluster != 0):
                    self.EmptyMyClusters()
                self.dir_firstCluster = 0
            me2 = self.GetMyDirectoryEntry()
            if (self.parent != None):
                self.parent.updateContent(me, me2)
                self.parent.writeDirectory()
            Mini_FAT.writeFAT()

    def ReadFileContent(self):
        if (self.dir_firstCluster != 0):
            cluster = self.dir_firstCluster
            nextClust = Mini_FAT.getClusterStatus(cluster)

            lst = bytes()
            while (cluster != -1):
                lst += Virtual_Disk.readCluster(cluster)
                cluster = nextClust
                if (cluster != -1):
                    nextClust=Mini_FAT.getClusterStatus(cluster)
            self.content = Converter.BytesToString(lst)

    def DeleteFile(self):
        self.EmptyMyClusters()
        if (self.parent != None):
            self.parent.removeEntry(self.GetMyDirectoryEntry())


    def PrintContent(self):
        print("\n" + self.dir_name+"\n")
        print(self.content)
        