import numpy as np

def randmat(X, DIM=None):
    # Check the number of dimensions
    if X.ndim > 2:
        raise ValueError("RANDMAT works for 1 or 2 dimensions only.")
    
    r, c = X.shape  # Get the shape of X
    
    if DIM is None or X.ndim == 1:  # If the input is 1D or DIM is not specified
        # Shuffle the entire array (like randperm), randomly shuffle each element
        I = np.random.permutation(np.arange(X.size))  # Random permutation of all indices
        Y = X.ravel()[I]  # Apply the permutation
        return Y, I
    
    elif DIM == 1:  # Shuffle rows (along the first axis) independently for each column
        Y = np.zeros_like(X)  # Initialize an empty array for the result
        I = np.zeros((c, r), dtype=int)  # Store indices of the random permutation for each column
        for i in range(c):  # Iterate over each column
            I[i, :] = np.random.permutation(r)  # Generate random permutation for the column
            Y[:, i] = X[I[i, :], i]  # Apply the permutation for the current column
        return Y, I.T  # Return the result and the indices (transposed to match the shape of X)
    
    elif DIM == 2:  # Shuffle columns (along the second axis) independently for each row
        Y = np.zeros_like(X)  # Initialize an empty array for the result
        I = np.zeros((r, c), dtype=int)  # Store indices of the random permutation for each row
        for i in range(r):  # Iterate over each row
            I[i, :] = np.random.permutation(c)  # Generate random permutation for the row
            Y[i, :] = X[i, I[i, :]]  # Apply the permutation for the current row
        return Y, I  # Return the result and the indices

    else:
        raise ValueError("DIM must be 1 or 2.")