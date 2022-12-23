#https://academic.oup.com/sysbio/article/63/5/685/2847738
Test.Kmult<-function(x,phy,iter=999){ 
    library(ape) 
    Kmult<-function(x,phy){ 
        x<-as.matrix(x) 
        N<-length(phy$tip.label)
        ones<-array(1,N) 
        C<-vcv.phylo(phy) 
        C<-C[row.names(x),row.names(x)] 
        a.obs<-colSums(solve(C))%*%x/sum(solve(C)) 
        #evol.vcvcode 
        distmat<-as.matrix(dist(rbind(as.matrix(x),a.obs))) 
        MSEobs.d<-sum(distmat[(1:N),(N+1)]ˆ2) 
        #sumdistancesrootvs.tips 
        eigC<-eigen(C) 
        D.mat<-solve(eigC$vectors 
            %*%diag(sqrt(eigC$values)) 
            %*%t(eigC$vectors)) 
        dist.adj<-as.matrix(dist(rbind((D.mat 
            %*%(x-(ones%*%a.obs))),0))) 
        MSE.d<-sum(dist.adj[(1:N),(N+1)]ˆ2) 
        #sumdistancesfortransformeddata) 
        K.denom<-(sum(diag(C))
        N*solve(t(ones)%*%solve(C)%*%ones))/(N-1) 
        K.stat<-(MSEobs.d/MSE.d)/K.denom 
        return(K.stat) } 
    K.obs<-Kmult(x,phy) 
    P.val<-1 
    K.val<-rep(0,iter) 
    for(iin1:iter){ 
        x.r<-as.matrix(x[sample(nrow(x)),]) 
        rownames(x.r)<-rownames(x) 
        K.rand<-Kmult(x.r,phy) 
        P.val<-ifelse(K.rand>=K.obs,P.val+1,P.val) 
        K.val[i]<-K.rand } 
    P.val<-P.val/(iter+1) 
    K.val[iter+1]=K.obs 
    hist(K.val,30,freq=TRUE,col="gray", xlab="PhylogeneticSignal") 
    arrows(K.obs,50,K.obs,5,length=0.1,lwd=2) 
    return(list(phy.signal=K.obs,pvalue=P.val)) }