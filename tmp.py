############################################
num_fields = 6 # Warehouse places 2x2 = 4 ..
############################################

num_color = 4 # empty, red, white,
# blue
num_moves = 6 # store red, store white, store blue, restore red, ...
num_actions = num_fields
block_size = num_color ** num_fields

num_state = num_color ** num_fields * num_moves
warehouse_description=[0,1,2,3] #possible colors

#Init TPM
P = []

for action in range(num_actions):
    current_index = 0
    P.append(np.zeros((num_state, num_state),dtype=np.float16))

    for instr in range(num_moves):
        for w_state in itertools.product(warehouse_description, repeat=num_fields):
            #Iter through all 6 column blocks (=possible instructions) (store red, store blue, ...., restore red, ...)
            for move in range(num_moves):

                ##For field one (Action)
                #FOR STORE
                if(instr in range(3)):

                    #1. Empty? if (field1 == 0)
                    if(w_state[action] != 0):
                        P[action][current_index][(current_index % block_size) + (block_size * move)] = move_probs[move]
                    else:
                        #FOR STORE
                        #if(red) index+64 (i**numFields)
                        # else if(white) index+128
                        # else if(blue) index+192

                        #red = 0
                        if(instr == 0):
                            P[action][current_index][((current_index % block_size) + (num_color**(num_actions - action - 1) * 1)) + (block_size * move)] = move_probs[move]
                        #white = 1
                        elif(instr == 1):
                            P[action][current_index][((current_index % block_size) + (num_color**(num_actions - action - 1) * 2)) + (block_size * move)] = move_probs[move]
                        #blue = 2
                        elif(instr == 2):
                            P[action][current_index][((current_index % block_size) + (num_color**(num_actions - action - 1) * 3)) + (block_size * move)] = move_probs[move]


                #FOR RESTORE
                else:
                    #possible? if (field 1 != 0)
                    if(w_state[action] == 0):
                        P[action][current_index][(current_index % block_size) + (block_size * move)] = move_probs[move]
                    else:
                        #FOR STORE
                        #if(red) index-64 (i**numFields)
                        # else if(white) index-128
                        # else if(blue) index-192

                        #red = 3
                        if(instr == 3):
                            P[action][current_index][((current_index % block_size) - (num_color**(num_actions - action - 1) * 1)) + (block_size * move)] = move_probs[move]
                        #white = 4
                        elif(instr == 4):
                            P[action][current_index][((current_index % block_size) - (num_color**(num_actions - action - 1) * 2)) + (block_size * move)] = move_probs[move]
                        #blue = 5
                        elif(instr == 5):
                            P[action][current_index][((current_index % block_size) - (num_color**(num_actions - action - 1) * 3)) + (block_size * move)] = move_probs[move]

            current_index += 1

    P[action] = sparse.csr_matrix(P[action])
    print("finished P"+str(action))

print("---")
print("successfull")

warehouse = []
for instr in range(num_moves):
    for w_state in itertools.product(warehouse_description, repeat=num_fields):
        tmp = []
        tmp_str = []
        for i in range(num_fields):
            tmp.append(w_state[i])
            tmp_str.append('state'+str(i))
        tmp.append(instr)
        tmp_str.append('NextMove')
        warehouse.append(tmp)

warehouse = pd.DataFrame(warehouse, columns=tmp_str)
print(warehouse.head())

R = []

for action in range(num_actions):
    R.append(np.zeros((num_state, )))

    for index, ws in warehouse.iterrows():
        try:
            #Reward for correct move
            if((ws.NextMove in range(3) and ws[action] == 0) or
            (ws.NextMove in range(3, 6) and (ws[action] == (ws.NextMove - 2)))):

                if  (action == 0): reward = 80**2  #8**3.5;
                elif(action == 1): reward = 60**2  #6**3.5;
                elif(action == 2): reward = 60**2  #6**3.5;
                elif(action == 3): reward = 40**2  #4**3.5;
                elif(action == 4): reward = 40**2  #4**3.5;
                elif(action == 5): reward = 40**2  #2**3.5;

                #Extra reward if restore is possible
                if ws.NextMove in range(3, 6) and (ws[action] == (ws.NextMove - 2)):
                    reward *= 100  #+=100

            #Reward for Failed moves
            else:
                #store not possible
                if ws.NextMove in range(3):
                    reward = -20000  #5
                #restore not possible
                else:
                    reward = -1000000  #-10

            R[-1][index] = reward

        except:
            print("An exception occurred")
            print(ws.NextMove)
            print(ws[action])

R = np.asarray(R)
R = R.transpose()