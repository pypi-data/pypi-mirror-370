"""
Loss function utilities for model loading.
"""

def get_loss_functions():
    """Get loss functions with on-demand imports"""
    try:
        from neutrophils_core.metrics.loss_functions import (
            categorical_crossentropy,
            categorical_dice_loss,
            get_loss_function
        )
        # Create wrapped loss functions for compatibility
        def weighted_categorical_crossentropy(weights):
            def loss(y_true, y_pred):
                return categorical_crossentropy(y_true, y_pred, class_weights=weights)
            return loss
        
        def weighted_dice_loss(weights):
            def loss(y_true, y_pred):
                return categorical_dice_loss(y_true, y_pred, class_weights=weights)
            return loss
        
        def weighted_f1_loss(weights):
            # F1 loss not available, use categorical crossentropy as fallback
            def loss(y_true, y_pred):
                return categorical_crossentropy(y_true, y_pred, class_weights=weights)
            return loss
        
        return {
            "ce": weighted_categorical_crossentropy,
            "dice": weighted_dice_loss,
            "f1": weighted_f1_loss
        }
        
    except ImportError:
        # Fallback - create basic loss functions
        import tensorflow as tf
        
        def weighted_categorical_crossentropy(weights):
            def loss(y_true, y_pred):
                return tf.keras.losses.categorical_crossentropy(y_true, y_pred)
            return loss
        
        def weighted_dice_loss(weights):
            def loss(y_true, y_pred):
                return tf.keras.losses.categorical_crossentropy(y_true, y_pred)
            return loss
            
        def weighted_f1_loss(weights):
            def loss(y_true, y_pred):
                return tf.keras.losses.categorical_crossentropy(y_true, y_pred)
            return loss
        
        return {
            "ce": weighted_categorical_crossentropy,
            "dice": weighted_dice_loss,
            "f1": weighted_f1_loss
        }