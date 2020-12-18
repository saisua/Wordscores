require(quanteda)
require(quanteda.textmodels)
#require(quanteda.corpora)
require(rlist)
require(stringr)
require(tm)
require(sets)
require(numbers)
require(ggplot2)
require(purrr)

folders <- c("./texts/pp2", "./texts/psoe2")
folnames <- c("PP", "PSOE")
files <- c()
docs <- c()

words_per_folder <- c()
total_words_per_folder <- rep(c(0), length(folders))
files_per_folder <- rep(c(0), length(folders))

uwords <- set()

count_words_per_folder <- list()
for(index in 1:length(folders)){
    count_words_per_folder[[index]] <- list()
}

count <- 0
difference <- Inf
#corp_ger <- list()
for(folder in folders){
    count <- count + 1

    file_list = list.files(folder)

    print(paste("Importing", length(list.files(folder)),"files from", folder))
    for(filenum in 1:length(file_list)){
        file = file_list[filenum]
        filename <- paste(folder,'/',file, sep='')
        doc <- readChar(filename, file.info(filename)$size)
        #doc <- str_replace_all(doc, "[`~ºª!|\"@·#$~%½€&¬\\/{()}=?¿\\[\\]^\\*+`´¨\\-.,_:;<>'•]", ' ')

        words <- strsplit(str_replace_all(doc, "[\n]", ' '), ' ')[[1]]

        if(total_words_per_folder[2] != 0){
            if(abs(total_words_per_folder[2]-total_words_per_folder[1]) < difference){
                difference = abs(total_words_per_folder[2]-total_words_per_folder[1])
            } else {
                print(paste("Removing", length(file_list) - filenum, "docs from group 2"))
                difference <- -1
                break
            }
        }

        files <- c(files, substr(file,0,20))
        docs <- c(docs, doc)
        files_per_folder[count] <- files_per_folder[count] + 1

        w_counter <- total_words_per_folder[count]

        if(is.null(w_counter) || is.na(w_counter)){
            total_words_per_folder <- c(total_words_per_folder, length(words))
        } else {
            total_words_per_folder[count] <- w_counter + length(words)
        }

        words_per_folder <- c(words_per_folder, as.list(words))

        uwords <- set_union(uwords, as.set(words))


        w_dict <- count_words_per_folder[[count]]
        for(word in words){
            w_count = w_dict[[word]]

            # Srsly lists are immutable?!?!??
            if(is.null(w_count))
                count_words_per_folder[[count]][[word]] <- 1
            else
                count_words_per_folder[[count]][[word]] <- w_count + 1
        }
        #print(count_words_per_folder[[count]])
    }
}

# If the for didnt break, chances are files[2] is smaller than files[1]
if(difference >= 0){
    words2 <- total_words_per_folder[2]
    difference <- words2
    val <- 0

    for(count in 1:files_per_folder[1]){
        valwc <- val + length(words_per_folder[count])

        #print(paste(count, difference, abs(words2 - valwc), length(words_per_folder[count])))

        if(difference < abs(words2 - valwc)){ 
            difference <- -1 
            break 
        }

        difference <- abs(words2 - valwc)
        val <- valwc
    }

    # if broke (+-)
    if(difference == -1){
        print(paste("Removing", files_per_folder[1] - count + 1, "docs from group 1"))
        docs <- docs[-c(count:files_per_folder[1])]
        files_per_folder[1] <- count - 1
    }
}

# Free memory
rm(folders, count, words_per_folder, w_counter, difference, file_list, filenum)
uwords <- length(uwords)
#

if(files_per_folder[1] > files_per_folder[2]){
    minim <- files_per_folder[2]
    maxi <- files_per_folder[1]

    num <- minim + 1
    base <- 1
    fin <- maxi

    rem <- 1
    irem <- 2
} else {
    minim <- files_per_folder[1]
    maxi <- files_per_folder[2]

    num <- minim*2 + 1
    base <- minim
    fin <- length(files)

    rem <- 2
    irem <- 1
}

inum <- num

while(num < fin){
    modulo <- mod(num, minim)

    docs[base+modulo] <- paste(docs[base+modulo], docs[num])

    num <- num + 1
}

print(files_per_folder)
docs <- docs[-c(inum:fin)]
files_per_folder[rem] <- files_per_folder[irem]

# Since no longer there are the same docs, i'll name them as its party
files <- c(rep(c("pp"), files_per_folder[1]), rep(c("psoe"), files_per_folder[2]))
for(file_num in 1:length(files)){
    files[file_num] <- paste(files[file_num], file_num)
}

print(paste("Merged", maxi-minim, files[base], "documents\nThere are", length(docs),"docs"))

#print(uwords)
print(total_words_per_folder)
print(files_per_folder)

# free memory
rm(total_words_per_folder, maxi, minim, modulo, num, inum, base, fin)
#
all_docs <- docs

input_folder <- "./texts/input/"
for(file in c("asrOutput_clean.txt", "Ana_Rosa01.10.2020_clean.txt")){
    filename <- paste(input_folder, file, sep='')
    all_docs <- c(all_docs, readChar(filename, file.info(filename)$size))
    files <- c(files, file)
}

ref_score <- c(rep(c(1), files_per_folder[1]), rep(c(-1), files_per_folder[2]), rep(NA, length(all_docs)-length(docs)))

#corp_init <- readRDS("./Coses_fallides/R_files/data.rds")
#my_data <- read.delim("./texts/pp/20-01-02_pp_actualidad-politica.txt")

# List<character>[12] { Documents }
# $ref_score : All docs scores, virgin score = NA
# List docvars()[3] {year, pary, ref_score}

# Words to remove
to_remove = c()

# create a document-feature matrix
dfmat_ger <- dfm(all_docs, remove=c(stopwords("es"), to_remove), remove_punct = TRUE)

# apply Wordscores algorithm to document-feature matrix
tmod_ws <- textmodel_wordscores(dfmat_ger, y = ref_score, smooth = 1)

#summary(tmod_ws)
#print(attributes(tmod_ws))

pred_ws <- predict(tmod_ws, se.fit = FALSE, newdata = dfmat_ger)

print(paste("Percentage of words used (approx):", length(tmod_ws$wordscores), "/", uwords , length(tmod_ws$wordscores) / uwords))

print(pred_ws)

print("\n\n### Printing results...\n")

# Return word distribution as pdf
count <- 1

max_amount <- 20
max_len <- max(unlist(map(count_words_per_folder, length)))
print(paste("Pdf of max length ", max_len, " in batch sizes ", max_amount))

for(file in count_words_per_folder){
    pdf(file=paste("WordDistributionFile_", folnames[count],".pdf"), 
        title="Word distribution per folder", colormodel="grey",
        onefile=TRUE
    )


    # Sort it
    file <- file[order(unlist(file), decreasing=TRUE)]


    sublists <- ceiling(length(file)/max_amount)
    for(sublist in 0:(sublists-1)){
        sub <- file[(sublist*max_amount):((sublist+1)*max_amount)]
        usub <- unlist(sub)
        sub <- sub[1:length(usub)]
        stripchart(sub, 
                    dlab=paste("Words of ", folnames[count]), 
                    pch="+", xlim=c(usub[length(usub)]-1, usub[1]+1))
        text(usub+c(rep(c(-0.5),ceiling(length(usub)/2)), rep(c(0.5), floor(length(usub)/2))),  
                1:length(usub), labels=names(usub))
    }

    count <- count + 1


    dev.off()
}

#warnings()

textplot_scale1d(pred_ws, doclabels=files, sort=TRUE)