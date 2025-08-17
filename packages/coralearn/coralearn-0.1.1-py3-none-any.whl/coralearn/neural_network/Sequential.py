class Sequential():
    def __init__(self, layers):
        self.loss = None
        self.layers = layers

    def forward(self, X):
        for layer in self.layers:
            X = layer.forward(X)
        return X

    def compile(self, loss):
        self.loss = loss

    def backward(self, loss_grad, lr=0.01):
        # go backwards through the layers
        for layer in reversed(self.layers):
            loss_grad = layer.backward(loss_grad, lr)
        return loss_grad

    def train(self, X, y, epochs=100, lr=0.01):
        for epoch in range(epochs):
            # forward
            y_pred = self.forward(X)

            # get loss and gradient
            loss_val, loss_grad = self.loss(y,y_pred)

            # backward pass
            self.backward(loss_grad, lr)

            #print every 100 epochs the value
            if epoch % 100 == 0:
                print(f"Epoch {epoch}, Loss = {loss_val:.4f}")