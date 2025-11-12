import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.mockito.InjectMocks;
import org.mockito.Mockito;

package com.ai_agent.app.reviewed;

import com.ai_agent.app.entity.Product;
import com.ai_agent.app.repository.ProductRepository;
import org.junit.jupiter.api.*;
import org.mockito.Mock;
import org.mockito.MockitoAnnotations;
import java.util.Arrays;
import java.util.List;
import static org.mockito.ArgumentMatchers.anyLong;
import static org.mockito.Mockito.*;

@DisplayName("ProductService Test")
public class ProductServiceTest {

    @Mock
    private ProductRepository productRepository;

    private ProductService productService;

    @BeforeEach
    public void setup() {
        MockitoAnnotations.initMocks(this);
        productService = new ProductService(productRepository);
    }

    @Test
    @DisplayName("Test getAllProducts")
    public void testGetAllProducts() {
        List<Product> products = Arrays.asList(new Product(), new Product());
        when(productRepository.findAll()).thenReturn(products);

        Assertions.assertEquals(products, productService.getAllProducts());
        verify(productRepository).findAll();
    }

    @Test
    @DisplayName("Test getProduct by id")
    public void testGetProductById() {
        Product product = new Product(1L);
        when(productRepository.findById(anyLong())).thenReturn(java.util.Optional.of(product));

        Assertions.assertEquals(product, productService.getProduct(1L));
        verify(productRepository).findById(1L);
    }

    @Test
    @DisplayName("Test saveProduct")
    public void testSaveProduct() {
        Product newProduct = new Product(1L);
        when(productRepository.save(newProduct)).thenReturn(newProduct);

        Product savedProduct = productService.saveProduct(newProduct);
        Assertions.assertEquals(newProduct, savedProduct);
        verify(productRepository).save(newProduct);
    }

    @Test
    @DisplayName("Test deleteProduct")
    public void testDeleteProduct() {
        Long id = 1L;
        productService.deleteProduct(id);
        verify(productRepository).deleteById(id);
    }
}
